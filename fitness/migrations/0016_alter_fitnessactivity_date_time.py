# Generated by Django 5.1.1 on 2024-12-19 12:14

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fitness", "0015_remove_fitnessactivity_intensity_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fitnessactivity",
            name="date_time",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]