# Generated by Django 3.1.7 on 2021-03-27 15:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
        ('geochats', '0009_auto_20210318_2252'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='geochats_anonmessage_message', to='geochats.chat')),
                ('username', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.username')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AuthMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='geochats_authmessage_message', to='geochats.chat')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]
