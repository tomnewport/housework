# Generated by Django 4.2.7 on 2023-11-18 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("teams", "0001_initial"),
        ("jobs", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobconfig",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="job_configs",
                to="teams.team",
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="assignee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assigned_jobs",
                to="teams.membership",
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="completed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="completed_jobs",
                to="teams.membership",
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="job_config",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="jobs.jobconfig",
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="teams.team"
            ),
        ),
        migrations.AddField(
            model_name="credit",
            name="job",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="credits",
                to="jobs.job",
            ),
        ),
        migrations.AddField(
            model_name="credit",
            name="person",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="teams.membership"
            ),
        ),
    ]
