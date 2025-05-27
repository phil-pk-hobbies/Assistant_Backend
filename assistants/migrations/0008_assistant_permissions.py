from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

def set_default_owner(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    Assistant = apps.get_model('assistants', 'Assistant')
    user = User.objects.first()
    if not user:
        user = User.objects.create(username='placeholder')
    Assistant.objects.filter(owner__isnull=True).update(owner=user)

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('org', '0001_initial'),
        ('assistants', '0007_alter_assistant_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='assistant',
            name='owner',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='owned_assistants',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name='AssistantUserAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.CharField(max_length=4, choices=[('use', 'Use'), ('edit', 'Edit')])),
                ('assistant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_access', to='assistants.assistant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assistant_access', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('assistant', 'user')}},
        ),
        migrations.CreateModel(
            name='AssistantDepartmentAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.CharField(max_length=4, choices=[('use', 'Use'), ('edit', 'Edit')])),
                ('assistant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dept_access', to='assistants.assistant')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assistant_access', to='org.department')),
            ],
            options={'unique_together': {('assistant', 'department')}},
        ),
        migrations.RunPython(set_default_owner, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='assistant',
            name='owner',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='owned_assistants',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
