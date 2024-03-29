# Generated by Django 3.1.7 on 2021-03-27 16:39

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('geochats', '0011_auto_20210327_1617'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='anonmessage',
            options={},
        ),
        migrations.AlterModelOptions(
            name='authmessage',
            options={},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={},
        ),
        migrations.RemoveField(
            model_name='anonmessage',
            name='chat',
        ),
        migrations.RemoveField(
            model_name='anonmessage',
            name='date',
        ),
        migrations.RemoveField(
            model_name='anonmessage',
            name='text',
        ),
        migrations.RemoveField(
            model_name='authmessage',
            name='chat',
        ),
        migrations.RemoveField(
            model_name='authmessage',
            name='date',
        ),
        migrations.RemoveField(
            model_name='authmessage',
            name='text',
        ),
        migrations.RemoveField(
            model_name='message',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='message',
            name='created',
        ),
        migrations.RemoveField(
            model_name='message',
            name='object_id',
        ),
        migrations.AddField(
            model_name='anonmessage',
            name='message',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='geochats.message'),
        ),
        migrations.AddField(
            model_name='authmessage',
            name='message',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='geochats.message'),
        ),
        migrations.AddField(
            model_name='message',
            name='chat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='geochats.chat'),
        ),
        migrations.AddField(
            model_name='message',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='text',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
