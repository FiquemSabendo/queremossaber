# Generated by Django 2.1.1 on 2018-09-07 10:38

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "foi_requests",
            "0009_extract_esic_from_publicbody_and_add_location_fields_to_it",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="message",
            old_name="title",
            new_name="summary",
        ),
    ]
