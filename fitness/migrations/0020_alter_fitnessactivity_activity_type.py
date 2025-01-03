# Generated by Django 5.1.1 on 2024-12-20 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fitness", "0019_userprofile_display_weight_alter_userprofile_weight"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fitnessactivity",
            name="activity_type",
            field=models.CharField(
                choices=[
                    ("RUN", "Running"),
                    ("YOG", "Yoga"),
                    ("CYC", "Cycling"),
                    ("STR", "Strength"),
                    ("WAL", "Walk"),
                    ("IBK", "Indoor Bike"),
                    ("TRE", "Treadmill"),
                    ("CAR", "Cardio Training"),
                ],
                max_length=3,
            ),
        ),
    ]