from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='threadfile',
            name='file_id',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
