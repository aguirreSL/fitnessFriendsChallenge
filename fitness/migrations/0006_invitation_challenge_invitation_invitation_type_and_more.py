# Generated by Django 5.1.1 on 2024-09-09 09:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitness', '0005_challenge_name_invitation'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='challenge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fitness.challenge'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='invitation_type',
            field=models.CharField(choices=[('Group', 'Group'), ('Challenge', 'Challenge')], default='Group', max_length=10),
        ),
        migrations.AlterField(
            model_name='invitation',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fitness.group'),
        ),
    ]
