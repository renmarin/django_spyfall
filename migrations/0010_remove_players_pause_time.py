# Generated by Django 3.2.6 on 2021-10-13 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spyfall', '0009_players_pause_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='players',
            name='pause_time',
        ),
    ]
