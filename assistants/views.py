"""
REST endpoints
--------------

/api/assistants/            CRUD
/api/messages/              read-only (handy for admin)
/api/assistants/<id>/chat/   POST {"content": "..."}  – send a message
/api/assistants/<id>/reset/  POST                     – clear conversation history
"""
import os
from django.http import JsonResponse
import time
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Assistant, Message
from .serializers import AssistantSerializer, MessageSerializer


# ──────────────────────────────────────────────────────────────────────────────
#  Assistants CRUD
# ──────────────────────────────────────────────────────────────────────────────
class AssistantViewSet(viewsets.ModelViewSet):
    """
    POST → also creates the remote assistant in OpenAI and stores its ID.
    """
    queryset = Assistant.objects.all()
    serializer_class = AssistantSerializer

    def perform_create(self, serializer):
        import openai

        data   = self.request.data
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 1️⃣  upload any attached files
        uploaded_file_ids: list[str] = []
        for f in self.request.FILES.getlist("files", []):
            resp = client.files.create(
                file=(f.name, f, f.content_type),
                purpose="assistants",
            )
            uploaded_file_ids.append(resp.id)

        # 2️⃣  build kwargs common to every assistant
        if hasattr(data, "getlist"):
            tools = data.getlist("tools") if "tools" in data else []
        else:
            tools = data.get("tools", []) or []
        tool_specs = [{"type": t} for t in tools]

        model_name = data.get("model", "gpt-4o")
        base_kwargs = dict(
            name=data.get("name", ""),
            description=data.get("description") or "",
            instructions=data.get("instructions") or "",
            model=model_name,
            tools=tool_specs,
        )

        # 3️⃣  attach files to the correct tool via tool_resources
        tool_resources = {}
        if uploaded_file_ids:
            if "code_interpreter" in tools:
                tool_resources["code_interpreter"] = {"file_ids": uploaded_file_ids}
            if "file_search" in tools:
                # create a vector store from the uploaded files and attach it
                vector_store = client.beta.vector_stores.create(
                    file_ids=uploaded_file_ids
                )
                tool_resources["file_search"] = {
                    "vector_store_ids": [vector_store.id]
                }
            # add other tool-resource mappings here if you support them

        if tool_resources:
            base_kwargs["tool_resources"] = tool_resources

        # 4️⃣  create the remote assistant
        oa_asst = client.beta.assistants.create(**base_kwargs)

        # 5️⃣  save locally
        serializer.save(
            openai_id=oa_asst.id,
            tools=tools,
            description=data.get("description") or "",
            model=model_name,
        )

    def perform_update(self, serializer):
        """Update both the local and remote assistant."""
        import openai

        instance = serializer.save()

        if instance.openai_id:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            client.beta.assistants.update(
                instance.openai_id,
                name=instance.name,
                description=instance.description or "",
                instructions=instance.instructions or "",
                model=instance.model,
                tools=[{"type": t} for t in instance.tools],
            )

    def perform_destroy(self, instance):
        """Delete the assistant locally and remotely in OpenAI."""
        import openai

        if instance.openai_id:
            try:
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                client.beta.assistants.delete(instance.openai_id)
            except Exception:
                pass
        instance.delete()


# ──────────────────────────────────────────────────────────────────────────────
#  Messages (read-only)
# ──────────────────────────────────────────────────────────────────────────────
class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        """Optionally filter messages by assistant via ?assistant=<uuid>."""
        qs = Message.objects.all()
        asst_id = self.request.query_params.get("assistant")
        if asst_id:
            qs = qs.filter(assistant_id=asst_id)
        return qs


# ──────────────────────────────────────────────────────────────────────────────
#  Chat endpoint
# ──────────────────────────────────────────────────────────────────────────────
class ChatView(APIView):
    """
    POST /api/assistants/<uuid>/chat/
    Body: {"content": "..."}
    """

    def post(self, request, pk):
        assistant = get_object_or_404(Assistant, pk=pk)
        user_msg  = request.data.get("content", "").strip()
        if not user_msg:
            return Response({"detail": "`content` field is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        # 🔹 1.  OpenAI client
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 🔹 2.  Make sure the assistant has a thread
        if not assistant.thread_id:
            thread = client.beta.threads.create()
            assistant.thread_id = thread.id
            assistant.save(update_fields=["thread_id"])

        # 🔹 3.  Store the user message locally *and* remotely
        Message.objects.create(
            assistant=assistant, role="user",
            content=user_msg, created_at=timezone.now()
        )
        client.beta.threads.messages.create(
            thread_id=assistant.thread_id,
            role="user",
            content=user_msg,
        )

        # 🔹 4.  Kick off a run (stream = False)
        run = client.beta.threads.runs.create(
            thread_id=assistant.thread_id,
            assistant_id=assistant.openai_id,
            stream=False,
        )

        # 🔹 5.  Poll until it finishes
        while run.status not in ("completed", "failed", "cancelled"):
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(
                thread_id=assistant.thread_id,
                run_id=run.id,
            )
        if run.status != "completed":
            return Response({"detail": f"Run ended with status '{run.status}'"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 🔹 6.  Get the assistant’s reply (most recent msg in the thread)
        msgs = client.beta.threads.messages.list(
            thread_id=assistant.thread_id, limit=1
        )
        assistant_msg = msgs.data[0].content[0].text.value

        # 🔹 7.  Persist it locally
        Message.objects.create(
            assistant=assistant, role="assistant",
            content=assistant_msg, created_at=timezone.now()
        )

        print(assistant_msg)

        # 🔹 8.  Return a normal JSON response
        return JsonResponse({"content": assistant_msg})


class ResetThreadView(APIView):
    """Delete all messages and remote thread for an assistant."""

    def post(self, request, pk):
        assistant = get_object_or_404(Assistant, pk=pk)
        thread_id = assistant.thread_id

        if thread_id:
            import openai
            try:
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                client.beta.threads.delete(thread_id)
            except Exception:
                pass

        assistant.messages.all().delete()
        assistant.thread_id = None
        assistant.save(update_fields=["thread_id"])

        return Response(status=status.HTTP_204_NO_CONTENT)
