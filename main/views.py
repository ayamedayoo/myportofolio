from django.contrib import messages
from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import AwardForm, ProjectForm
from main.models import Award, Experience, Project


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _json_response(queryset):
    """Serialize queryset ke JSON dan bungkus dalam HttpResponse."""
    return HttpResponse(
        serializers.serialize("json", queryset),
        content_type="application/json",
    )


def _deserialize(response):
    """Ubah HttpResponse JSON hasil ``_json_response`` kembali menjadi list objek model.

    Objek hasil deserialisasi tetap instance model biasa, jadi method seperti
    ``get_level_display`` dan property seperti ``is_ongoing`` tetap bisa dipakai di template.
    """
    return [item.object for item in serializers.deserialize("json", response.content)]


# ---------------------------------------------------------------------------
# Profile & Experience
# ---------------------------------------------------------------------------

def show_main(request):
    context = {
        "npm": "2506657333",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan. "
            "imut, tampan, gagah dan keren."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    """Render the experience page with a list of all experiences ordered by start date (newest first)."""
    context = {
        "experience_list": Experience.objects.all().order_by('-started_at'),
    }
    return render(request, "experience.html", context)


def get_experiences_json(request):
    """Kembalikan seluruh data experience dalam format JSON."""
    return _json_response(Experience.objects.all().order_by('-started_at'))


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

def show_project(request):
    """Render the project page from the JSON endpoint, optionally filtered by title."""
    projects = _deserialize(get_projects_json(request))
    context = {
        "project_list": projects,
        "title_query": request.GET.get("title", "").strip(),
    }
    return render(request, "project.html", context)


def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_project")
    return render(request, "project_form.html", {"form": form})


def update_project(request, project_id):
    """Ambil project berdasarkan id, tampilkan form berisi data lamanya, lalu simpan perubahannya."""
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Proyek \"{project.title}\" berhasil diperbarui!")
        return redirect("main:show_project")
    return render(request, "project_form.html", {"form": form, "project": project})


@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, "Proyek berhasil dihapus!")
    return redirect("main:show_project")


def get_projects_json(request):
    projects = Project.objects.all().order_by('-started_at')
    title_query = request.GET.get("title", "").strip()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    return _json_response(projects)


def get_project_json_by_id(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return _json_response([project])


# ---------------------------------------------------------------------------
# Award
# ---------------------------------------------------------------------------

def show_award(request):
    """Render halaman award.

    Datanya tidak diambil langsung dari ORM, melainkan dari ``get_awards_json``
    lalu dideserialisasi, sehingga halaman ini memakai data yang sama persis
    dengan yang dikirim endpoint JSON (termasuk filter ``level`` dan ``q``).
    """
    awards = _deserialize(get_awards_json(request))

    # Hanya tampilkan tombol filter untuk tingkat yang memang punya data.
    used_levels = set(Award.objects.values_list("level", flat=True))
    level_filters = [
        {"value": value, "label": label}
        for value, label in Award.LEVEL_CHOICES
        if value in used_levels
    ]

    # Level yang tidak dikenal diabaikan oleh get_awards_json, jadi chip "Semua" yang harus aktif.
    active_level = request.GET.get("level", "")
    if active_level not in dict(Award.LEVEL_CHOICES):
        active_level = ""

    context = {
        "award_list": awards,
        "level_filters": level_filters,
        "active_level": active_level,
        "search_query": request.GET.get("q", "").strip(),
    }
    return render(request, "award.html", context)


def create_award(request):
    form = AwardForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        award = form.save()
        messages.success(request, f"Penghargaan \"{award.title}\" berhasil ditambahkan!")
        return redirect("main:show_award")
    return render(request, "award_form.html", {"form": form})


def update_award(request, award_id):
    """Form update memakai ``instance`` agar field terisi data lama dan ``save()`` melakukan UPDATE, bukan INSERT."""
    award = get_object_or_404(Award, pk=award_id)
    form = AwardForm(request.POST or None, instance=award)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Penghargaan \"{award.title}\" berhasil diperbarui!")
        return redirect("main:show_award")
    return render(request, "award_form.html", {"form": form, "award": award})


@require_POST
def delete_award(request, award_id):
    award = get_object_or_404(Award, pk=award_id)
    title = award.title
    award.delete()
    messages.success(request, f"Penghargaan \"{title}\" berhasil dihapus.")
    return redirect("main:show_award")


def get_awards_json(request):
    """Kembalikan data award dalam JSON.

    Query parameter opsional:
    - ``level``: filter berdasarkan tingkat (``internal``, ``regional``, ``national``, ``international``)
    - ``q``: cari berdasarkan nama penghargaan atau penyelenggara
    """
    awards = Award.objects.all()

    level = request.GET.get("level", "")
    if level in dict(Award.LEVEL_CHOICES):
        awards = awards.filter(level=level)

    query = request.GET.get("q", "").strip()
    if query:
        awards = awards.filter(Q(title__icontains=query) | Q(issuer__icontains=query))

    return _json_response(awards)


def get_award_json_by_id(request, award_id):
    award = get_object_or_404(Award, pk=award_id)
    return _json_response([award])
