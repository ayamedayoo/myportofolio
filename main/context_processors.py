"""Context processor supaya data identitas pemilik portofolio tersedia di semua template.

Sebelumnya setiap view menulis ulang ``"name": "Samuel Kaevin Phasca"`` di context-nya.
Dengan context processor ini, ``{{ name }}`` di ``base.html`` otomatis terisi.
"""

from main import roles

OWNER_NAME = "Samuel Kaevin Phasca"


def portfolio_owner(request):
    return {"name": OWNER_NAME}


def user_roles(request):
    """Kirim hak akses pengguna ke semua template, dipakai untuk menyembunyikan tombol aksi."""
    user = request.user
    return {
        "is_editor": roles.is_editor(user),
        "can_create": roles.can_create(user),
        "can_update": roles.can_update(user),
        "can_delete": roles.can_delete(user),
    }
