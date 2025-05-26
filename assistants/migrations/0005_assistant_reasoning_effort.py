from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('assistants', '0004_assistant_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='assistant',
            name='reasoning_effort',
            field=models.CharField(
                max_length=6,
                choices=[('low', 'low'), ('medium', 'medium'), ('high', 'high')],
                default='medium',
            ),
        ),
    ]
