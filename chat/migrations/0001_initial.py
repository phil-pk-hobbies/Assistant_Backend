from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assistants', '0008_assistant_permissions'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('openai_id', models.CharField(blank=True, max_length=64, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assistant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='threads', to='assistants.assistant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='threads', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('assistant', 'user')},
            },
        ),
        migrations.CreateModel(
            name='ThreadFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('original_name', models.CharField(max_length=255)),
                ('file_id', models.CharField(max_length=64)),
                ('size_bytes', models.BigIntegerField()),
                ('mime_type', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('uploading', 'Uploading'), ('ready', 'Ready'), ('error', 'Error')], default='uploading', max_length=10)),
                ('error_reason', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='chat.thread')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thread_files', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('thread', 'file_id')},
            },
        ),
        migrations.AddIndex(
            model_name='threadfile',
            index=models.Index(fields=['thread', 'status'], name='chat_thread_status_idx'),
        ),
        migrations.AddIndex(
            model_name='threadfile',
            index=models.Index(fields=['created_at'], name='chat_created_at_idx'),
        ),
    ]
