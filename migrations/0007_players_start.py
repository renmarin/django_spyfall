# Generated by Django 3.2.6 on 2021-10-04 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spyfall', '0006_remove_players_roles_ratio'),
    ]

    operations = [
        migrations.AddField(
            model_name='players',
            name='start',
            field=models.BooleanField(default=False),
        ),
    ]