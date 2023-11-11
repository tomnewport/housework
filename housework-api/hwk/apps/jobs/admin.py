from django.contrib import admin

from hwk.apps.jobs.models import JobVariant, JobConfig, Job, JobTrigger, JobScheduleRule


class JobVariantInline(admin.TabularInline):
    model = JobVariant
    extra = 1  # Number of empty forms to display


class JobConfigAdmin(admin.ModelAdmin):
    inlines = [JobVariantInline]


admin.site.register(JobConfig, JobConfigAdmin)
admin.site.register(JobVariant)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['name', 'due_date', 'status', 'assignee']
    list_filter = ['status', 'is_priority', 'due_date']
    search_fields = ['name', 'description']


@admin.register(JobTrigger)
class JobTriggerAdmin(admin.ModelAdmin):
    list_display = ['from_config', 'create_config', 'lifecycle', 'urgent']
    list_filter = ['lifecycle', 'urgent']
    search_fields = ['from_config__name', 'create_config__name']


@admin.register(JobScheduleRule)
class JobScheduleRuleAdmin(admin.ModelAdmin):
    list_display = ['trigger', 'rule_type']
    list_filter = ['rule_type']
    search_fields = ['trigger__name']