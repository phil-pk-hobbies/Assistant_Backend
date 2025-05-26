from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('assistants', '0005_assistant_reasoning_effort'),
    ]

    operations = [
        migrations.AddField(
            model_name='assistant',
            name='vector_store_id',
            field=models.CharField(max_length=40, blank=True, null=True),
        ),
    ]
