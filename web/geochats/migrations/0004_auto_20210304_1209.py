# Generated by Django 3.1.7 on 2021-03-04 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geochats', '0003_message'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PointCenter',
            new_name='Chat',
        ),
        migrations.DeleteModel(
            name='Elevation',
        ),
        migrations.DeleteModel(
            name='Zipcode',
        ),
    ]
