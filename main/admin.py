from django.contrib import admin

from main.models import Award, Experience, Project


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ("title", "issuer", "year", "placement", "level", "is_featured")
    list_filter = ("placement", "level", "is_featured")
    search_fields = ("title", "issuer")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "role", "started_at", "ended_at")
    search_fields = ("title",)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "started_at", "ended_at")
    list_filter = ("category",)
