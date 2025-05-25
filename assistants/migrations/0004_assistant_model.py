from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('assistants', '0003_assistant_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='assistant',
            name='model',
            field=models.CharField(default='gpt-4o', max_length=40),
        ),
    ]
