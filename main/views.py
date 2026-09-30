import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import AwardForm, ProjectForm
from main.roles import LOGIN_URL, can_create, can_delete, can_update, role_required
from main.models import Award, Experience, Project, Achievement


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _json_response(queryset):
    """Serialize queryset ke JSON dan bungkus dalam HttpResponse.

    ``use_natural_foreign_keys`` membuat relasi ke User (mis. ``starred_by``)
    ditulis sebagai username, bukan id internal database.
    """
    return HttpResponse(
        serializers.serialize("json", queryset, use_natural_foreign_keys=True),
        content_type="application/json",
    )


def _toggle_star(obj, user):
    """Beri star kalau belum pernah, batalkan kalau sudah. Satu pengguna maksimal satu star."""
    if obj.starred_by.filter(pk=user.pk).exists():
        obj.starred_by.remove(user)
    else:
        obj.starred_by.add(user)


def _deserialize(response):
    """Ubah HttpResponse JSON hasil ``_json_response`` kembali menjadi list objek model.

    Objek hasil deserialisasi tetap instance model biasa, jadi method seperti
    ``get_level_display`` dan property seperti ``is_ongoing`` tetap bisa dipakai di template.
    """
    return [item.object for item in serializers.deserialize("json", response.content)]


# ---------------------------------------------------------------------------
# Autentikasi
# ---------------------------------------------------------------------------

def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")
    return render(request, "register.html", {"form": form})


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        response.set_cookie("last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return response
    return render(request, "login.html", {"form": form})


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


# ---------------------------------------------------------------------------
# Profile & Experience
# ---------------------------------------------------------------------------

def show_main(request):
    last_login = request.COOKIES.get("last_login", "Belum ada sesi login / Cookie tidak ditemukan")
    context = {
        "npm": "2506657333",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan. "
            "imut, tampan, gagah dan keren."
        ),
        "last_login": last_login,
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
    """Render kerangka halaman project. Datanya diambil browser lewat AJAX dari ``get_projects_json``."""
    context = {
        "title_query": request.GET.get("title", "").strip(),
        # Form kosong untuk modal tambah proyek, hanya dipakai kalau pengguna boleh membuat data.
        "form": ProjectForm(),
    }
    return render(request, "project.html", context)


@role_required(can_create)
def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_project")
    return render(request, "project_form.html", {"form": form})


@role_required(can_update)
def update_project(request, project_id):
    """Ambil project berdasarkan id, tampilkan form berisi data lamanya, lalu simpan perubahannya."""
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Proyek \"{project.title}\" berhasil diperbarui!")
        return redirect("main:show_project")
    return render(request, "project_form.html", {"form": form, "project": project})


@role_required(can_delete)
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, "Proyek berhasil dihapus!")
    return redirect("main:show_project")


# Tanpa cek peran: semua akun yang sudah login boleh memberi star
@login_required(login_url=LOGIN_URL)
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        _toggle_star(project, request.user)
    return redirect("main:show_project")


@require_POST
def create_project_ajax(request):
    """Tambah proyek lewat AJAX. Balasannya selalu JSON supaya mudah dibaca JavaScript.

    Sengaja tidak memakai ``role_required``: dekorator itu mengalihkan pengunjung ke halaman
    login, dan ``fetch`` akan mengikuti pengalihan tersebut lalu menerima HTML berstatus 200.
    """
    if not can_create(request.user):
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


def get_projects_json(request):
    """Kembalikan daftar proyek dalam JSON, opsional difilter dengan ``?title=``.

    JSON dirakit manual karena ``serializers.serialize`` tidak bisa menyisipkan informasi
    yang bergantung pada pengguna yang sedang login, seperti ``is_starred``.
    """
    projects = Project.objects.prefetch_related("starred_by").order_by("-started_at")
    title_query = request.GET.get("title", "").strip()
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    data = []
    for project in projects:
        starred_usernames = [user.username for user in project.starred_by.all()]
        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "role": project.role,
                "started_at": project.started_at.isoformat(),
                "ended_at": project.ended_at.isoformat() if project.ended_at else None,
                "is_ongoing": project.is_ongoing,
                "star_count": len(starred_usernames),
                "is_starred": request.user.is_authenticated and request.user.username in starred_usernames,
                "starred_by_names": ", ".join(starred_usernames),
            },
        })
    return JsonResponse(data, safe=False)


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


@role_required(can_create)
def create_award(request):
    form = AwardForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        award = form.save()
        messages.success(request, f"Penghargaan \"{award.title}\" berhasil ditambahkan!")
        return redirect("main:show_award")
    return render(request, "award_form.html", {"form": form})


@role_required(can_update)
def update_award(request, award_id):
    """Form update memakai ``instance`` agar field terisi data lama dan ``save()`` melakukan UPDATE, bukan INSERT."""
    award = get_object_or_404(Award, pk=award_id)
    form = AwardForm(request.POST or None, instance=award)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Penghargaan \"{award.title}\" berhasil diperbarui!")
        return redirect("main:show_award")
    return render(request, "award_form.html", {"form": form, "award": award})


@role_required(can_delete)
@require_POST
def delete_award(request, award_id):
    award = get_object_or_404(Award, pk=award_id)
    title = award.title
    award.delete()
    messages.success(request, f"Penghargaan \"{title}\" berhasil dihapus.")
    return redirect("main:show_award")


@login_required(login_url=LOGIN_URL)
@require_POST
def toggle_award_star(request, award_id):
    award = get_object_or_404(Award, pk=award_id)
    _toggle_star(award, request.user)
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


# ---------------------------------------------------------------------------
# Achievement
# ---------------------------------------------------------------------------

def show_achievements(request):
    achievements = Achievement.objects.all().order_by('-achieved_at')
    context = {
        'achievements': achievements,
    }
    return render(request, 'achievements.html', context)
