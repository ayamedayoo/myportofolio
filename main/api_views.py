from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Award, Project
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly, IsPortfolioOwnerOrReadOnly
from main.serializers import AwardSerializer, ProjectSerializer


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    """GET: daftar proyek (opsional ``?title=``). POST: tambah proyek (pemilik)."""
    if request.method in ("GET", "HEAD"):
        projects = Project.objects.prefetch_related("starred_by").order_by("-started_at", "title", "id")
        title = request.query_params.get("title", "").strip()
        if title:
            projects = projects.filter(title__icontains=title)
        serializer = ProjectSerializer(
            projects, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ProjectSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    """GET: detail. PUT/PATCH: ubah. DELETE: hapus. Tindakan tulis hanya untuk pemilik."""
    project = get_object_or_404(
        Project.objects.prefetch_related("starred_by"), pk=project_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ProjectSerializer(
        project, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    """Toggle star milik akun yang sedang login, lalu kembalikan data proyek terbaru."""
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)


# ---------------------------------------------------------------------------
# Award (bagian portofolio Tugas 3-5)
# ---------------------------------------------------------------------------
# Hak akses mengikuti empat peran Tugas 4 lewat IsPortfolioOwnerOrEditorOrReadOnly:
# semua orang boleh membaca, Editor boleh PUT/PATCH, hanya pemilik yang boleh POST/DELETE.
# Validasi ada di AwardSerializer, jadi view hanya mengatur alur dan status HTTP.

def _award_queryset():
    """Award beserta pemberi star-nya, diambil dengan satu query tambahan untuk semua data."""
    return Award.objects.prefetch_related("starred_by")


def filter_awards(queryset, params, user):
    """Terapkan filter dari query parameter daftar award.

    - ``q``: cari di nama penghargaan atau penyelenggara (pindahan pencarian Tugas 5)
    - ``level``: tingkat lomba; nilai yang tidak dikenal diabaikan
    - ``starred=1``: hanya award yang diberi star oleh akun yang sedang login
    """
    query = params.get("q", "").strip()
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(issuer__icontains=query))

    level = params.get("level", "")
    if level in dict(Award.LEVEL_CHOICES):
        queryset = queryset.filter(level=level)

    if params.get("starred") == "1" and user.is_authenticated:
        queryset = queryset.filter(starred_by=user)
    return queryset


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def award_list(request):
    """GET: daftar award (opsional ``?q=``, ``?level=``, ``?starred=1``). POST: tambah award (pemilik)."""
    if request.method in ("GET", "HEAD"):
        awards = filter_awards(_award_queryset(), request.query_params, request.user)
        serializer = AwardSerializer(awards, many=True, context={"request": request})
        return Response(serializer.data)

    serializer = AwardSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def award_detail(request, award_id):
    """GET: detail. PUT/PATCH: ubah (Editor dan pemilik). DELETE: hapus (pemilik)."""
    award = get_object_or_404(_award_queryset(), pk=award_id)
    if request.method in ("GET", "HEAD"):
        return Response(AwardSerializer(award, context={"request": request}).data)

    if request.method == "DELETE":
        award.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = AwardSerializer(
        award, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def award_star(request, award_id):
    """Beri atau batalkan star milik ``request.user``, lalu kembalikan data award terbaru.

    Akun pemberi star tidak pernah dibaca dari body request, jadi seseorang tidak bisa
    memberi star atas nama akun lain.
    """
    award = get_object_or_404(Award, pk=award_id)
    if award.starred_by.filter(pk=request.user.pk).exists():
        award.starred_by.remove(request.user)
    else:
        award.starred_by.add(request.user)
    award = _award_queryset().get(pk=award.pk)  # ambil ulang agar cache star segar
    return Response(AwardSerializer(award, context={"request": request}).data)
