# Generated by Django 5.1.1 on 2024-12-16 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fitness", "0011_challenge_is_public_fitnessgroup_is_public"),
    ]

    operations = [
        migrations.AddField(
            model_name="invitation",
            name="status",
            field=models.CharField(default="Pending", max_length=20),
        ),
    ]
