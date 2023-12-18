# Generated by Django 5.0 on 2023-12-18 02:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0005_alter_mediafile_traffic_violation_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="trafficviolation",
            name="location",
        ),
        migrations.AddField(
            model_name="trafficviolation",
            name="address",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="trafficviolation",
            name="latitude",
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="trafficviolation",
            name="longtitude",
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="trafficviolation",
            name="user_input_type",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
