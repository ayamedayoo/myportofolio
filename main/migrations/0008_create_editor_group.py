"""Membuat grup "Editor" supaya tinggal diisi anggotanya lewat Django Admin.

Grup ini juga mendapat izin change_award dan change_project, jadi di halaman admin
terlihat jelas bahwa Editor hanya boleh mengubah data, tidak membuat atau menghapus.
"""

from django.contrib.auth.management import create_permissions
from django.db import migrations

EDITOR_PERMISSIONS = ["change_award", "change_project"]


def create_editor_group(apps, schema_editor):
    # Izin bawaan model baru dibuat setelah migrasi selesai, jadi dibuat lebih awal di sini.
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    group, _ = Group.objects.get_or_create(name="Editor")
    group.permissions.add(
        *Permission.objects.filter(content_type__app_label="main", codename__in=EDITOR_PERMISSIONS)
    )


def remove_editor_group(apps, schema_editor):
    apps.get_model("auth", "Group").objects.filter(name="Editor").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("main", "0007_award_starred_by"),
    ]

    operations = [
        migrations.RunPython(create_editor_group, remove_editor_group),
    ]
