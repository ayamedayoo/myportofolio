"""Aturan peran pengguna di website portofolio.

Ada empat peran:
- Pengunjung (belum login): hanya bisa membaca.
- Pengguna biasa: bisa membaca dan memberi star.
- Editor (anggota grup "Editor"): hak pengguna biasa, ditambah boleh mengubah data.
- Pemilik (superuser): boleh membuat, mengubah, dan menghapus data.

Semua pemeriksaan peran dikumpulkan di sini supaya view dan template memakai aturan yang sama.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

EDITOR_GROUP = "Editor"
LOGIN_URL = "/login/"


def is_editor(user):
    return user.is_authenticated and user.groups.filter(name=EDITOR_GROUP).exists()


def can_create(user):
    return user.is_superuser


def can_update(user):
    return user.is_superuser or is_editor(user)


def can_delete(user):
    return user.is_superuser


def role_required(check):
    """Dekorator view: pengunjung dialihkan ke login, pengguna yang tidak berhak mendapat 403."""
    def decorator(view_func):
        @login_required(login_url=LOGIN_URL)
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not check(request.user):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
