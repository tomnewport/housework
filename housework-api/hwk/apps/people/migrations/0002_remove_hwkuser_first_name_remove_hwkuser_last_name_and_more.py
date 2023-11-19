# Generated by Django 4.2.7 on 2023-11-18 14:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hwkuser",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="hwkuser",
            name="last_name",
        ),
        migrations.AddField(
            model_name="hwkuser",
            name="full_name",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name="hwkuser",
            name="short_name",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]