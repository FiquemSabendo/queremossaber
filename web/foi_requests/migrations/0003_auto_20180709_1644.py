# Generated by Django 2.0.2 on 2018-07-09 16:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("foi_requests", "0002_auto_20180328_1901"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="foirequest",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterModelOptions(
            name="message",
            options={"ordering": ["-created_at", "-moderation_status"]},
        ),
        migrations.RemoveField(
            model_name="foirequest",
            name="moderated_at",
        ),
        migrations.RemoveField(
            model_name="foirequest",
            name="moderation_message",
        ),
        migrations.RemoveField(
            model_name="foirequest",
            name="moderation_status",
        ),
        migrations.AddField(
            model_name="message",
            name="moderated_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="message",
            name="moderation_message",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="message",
            name="moderation_status",
            field=models.NullBooleanField(
                choices=[(None, "Pending"), (True, "Approved"), (False, "Rejected")]
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="sent_at",
            field=models.DateTimeField(null=True, verbose_name="Sent date"),
        ),
    ]
