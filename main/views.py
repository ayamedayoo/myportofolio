from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.core import serializers
from main.models import Experience, Project, Award
from main.forms import ProjectForm


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
    json_response = get_projects_json(request)
    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()
    
    context = {
        "name": "Samuel Kaevin Phasca",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "project.html", context)

def show_award(request):
    """Render the award page with a list of all awards ordered by year (newest first)."""
    context = {
        "name": "Samuel Kaevin Phasca",
        "award_list": Award.objects.all().order_by('-year'),
    }
    return render(request, "award.html", context)

def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_project")
    
    context = {
        "name": "Samuel Kaevin Phasca",
        "form": form,
    }
    return render(request, "project_form.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all().order_by('-started_at')
    
    if title_query:
        projects = projects.filter(title__icontains=title_query)
        
    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_project")
    return redirect("main:show_project")