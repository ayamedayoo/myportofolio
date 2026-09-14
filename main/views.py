from django.shortcuts import render

from main.models import Experience, Project, Award


def show_main(request):
    context = {
        "name": "Samuel Kaevin Phasca",
        "npm": "2506657333",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
            "imut, tampan, gagah dan keren."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    """Render the experience page with a list of all experiences ordered by start date (newest first)."""
    context = {
        "name": "Samuel Kaevin Phasca",
        "experience_list": Experience.objects.all().order_by('-started_at'),
    }
    return render(request, "experience.html", context)

def show_project(request):
    """Render the project page with a list of all projects ordered by start date (newest first)."""
    context = {
        "name": "Samuel Kaevin Phasca",
        "project_list": Project.objects.all().order_by('-started_at'),
    }
    return render(request, "project.html", context)

def show_award(request):
    """Render the award page with a list of all awards ordered by year (newest first)."""
    context = {
        "name": "Samuel Kaevin Phasca",
        "award_list": Award.objects.all().order_by('-year'),
    }
    return render(request, "award.html", context)