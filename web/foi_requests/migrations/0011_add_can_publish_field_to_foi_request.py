# Generated by Django 2.1.1 on 2018-09-21 15:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("foi_requests", "0010_rename_message_title_to_summary"),
    ]

    operations = [
        migrations.AddField(
            model_name="foirequest",
            name="can_publish",
            field=models.BooleanField(default=False),
        ),
    ]
