# Generated by Django 2.0.2 on 2018-07-10 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foi_requests', '0005_add_message_contraint_to_avoid_rejections_without_message_20180709_1846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='moderated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Sent date'),
        ),
    ]