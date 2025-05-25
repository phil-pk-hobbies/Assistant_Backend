from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('assistants', '0002_assistant_openai_id_assistant_thread_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='assistant',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]

