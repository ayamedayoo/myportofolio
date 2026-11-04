from rest_framework.permissions import SAFE_METHODS, BasePermission

from main.roles import EDITOR_GROUP


class IsPortfolioOwnerOrReadOnly(BasePermission):
    """Semua orang boleh membaca; hanya pemilik (superuser) yang boleh mengubah."""

    message = "Hanya pemilik portofolio yang dapat mengubah proyek."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
        )


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """Seperti di atas, tetapi anggota grup Editor juga boleh PUT/PATCH (aturan Tugas 4)."""

    message = "Kamu tidak memiliki izin untuk melakukan tindakan ini."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return (
            request.method in ("PUT", "PATCH")
            and request.user.groups.filter(name=EDITOR_GROUP).exists()
        )
