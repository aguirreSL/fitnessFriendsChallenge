# Generated by Django 5.1.1 on 2024-12-19 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fitness", "0016_alter_fitnessactivity_date_time"),
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
                    ("CAR", "Cardio Trainning"),
                ],
                max_length=3,
            ),
        ),
    ]
