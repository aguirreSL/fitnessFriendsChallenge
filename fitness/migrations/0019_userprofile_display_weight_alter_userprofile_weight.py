# Generated by Django 5.1.1 on 2024-12-19 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fitness", "0018_alter_fitnessactivity_calories_burned"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="display_weight",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="weight",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
