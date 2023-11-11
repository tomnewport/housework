# Generated by Django 4.2.7 on 2023-11-11 14:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('policy_when_on_holiday', models.CharField(choices=[('FIND_OTHER', 'Try to find another assignee'), ('WHEN_BACK', 'Give to first assignee when back')], max_length=16)),
                ('policy_max_team_diff', models.PositiveSmallIntegerField(default=600, help_text='Maximum relative credit in team to consider for job assigner')),
                ('policy_max_job_diff', models.PositiveSmallIntegerField(default=120, help_text='Maximum relative credit on a job to consider for job assigner')),
                ('policy_team_credit_weight', models.PositiveSmallIntegerField(help_text='Weight given to relative credit within the team')),
                ('policy_job_credit_weight', models.PositiveSmallIntegerField(help_text='Weight given to relative credit on each job')),
                ('policy_random_weight', models.PositiveSmallIntegerField(help_text='Random weighting')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('Member', 'Member'), ('Applicant', 'Applicant'), ('Admin', 'Admin')], max_length=10)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='teams.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
