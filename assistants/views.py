"""
REST endpoints
--------------

/api/assistants/            CRUD
/api/messages/              read-only (handy for admin)
/api/assistants/<id>/chat/  POST {"content": "..."}  – streams the assistant reply
"""
import os
import openai

from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

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
        tools      = data.getlist("tools") if "tools" in data else []
        tool_specs = [{"type": t} for t in tools] or None

        base_kwargs = dict(
            name=data.get("name", ""),
            description=data.get("description") or "",
            instructions=data.get("instructions") or "",
            model=data.get("model", "gpt-4o"),
            tools=tool_specs,
        )

        # 3️⃣  attach files to the correct tool via tool_resources
        tool_resources = {}
        if uploaded_file_ids:
            if "code_interpreter" in tools:
                tool_resources["code_interpreter"] = {"file_ids": uploaded_file_ids}
            # add other tool-resource mappings here if you support them
            # (e.g. vector_store IDs for file_search)

        if tool_resources:
            base_kwargs["tool_resources"] = tool_resources

        # 4️⃣  create the remote assistant
        oa_asst = client.beta.assistants.create(**base_kwargs)

        # 5️⃣  save locally
        serializer.save(
            openai_id=oa_asst.id,
            tools=tools,
        )


# ──────────────────────────────────────────────────────────────────────────────
#  Messages (read-only)
# ──────────────────────────────────────────────────────────────────────────────
class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


# ──────────────────────────────────────────────────────────────────────────────
#  Chat endpoint
# ──────────────────────────────────────────────────────────────────────────────
class ChatView(APIView):
    """
    POST /api/assistants/<uuid>/chat/
    Body: {"content": "..."}
    Streams the assistant’s reply back as Server-Sent Events (SSE).
    """

    def post(self, request, pk):
        assistant = get_object_or_404(Assistant, pk=pk)

        user_msg = request.data.get("content", "").strip()
        if not user_msg:
            return Response({"detail": "`content` field is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 1️⃣  guarantee we have a thread
        if not assistant.thread_id:
            thread = client.beta.threads.create()
            assistant.thread_id = thread.id
            assistant.save(update_fields=["thread_id"])

        # 2️⃣  add the user’s message
        client.beta.threads.messages.create(
            thread_id=assistant.thread_id,
            role="user",
            content=user_msg,
        )

        # 3️⃣  run & stream deltas
        run_stream = client.beta.threads.runs.create(
            thread_id=assistant.thread_id,
            assistant_id=assistant.openai_id,
            stream=True,
        )

        def sse_events():
            """Yield only the message deltas from the streaming run."""
            for chunk in run_stream:
                # The stream returns many event types.  Only ``thread.message.delta``
                # events contain the incremental content from the assistant.  Skip
                # all other events to avoid attribute errors like ``ThreadRunCreated``
                # having no ``delta`` attribute.
                if getattr(chunk, "event", None) == "thread.message.delta":
                    text = getattr(chunk.data.delta, "content", "") or ""
                    if text:
                        yield f"data: {text}\n\n"

        return StreamingHttpResponse(
            streaming_content=sse_events(),
            content_type="text/event-stream",
        )
