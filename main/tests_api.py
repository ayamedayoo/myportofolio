import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Award, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", role="Fullstack Developer",
            started_at="2026-08-01",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "role": "Backend Developer",
            "started_at": "2026-09-01", "ended_at": None,
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertTrue(response.data[0]["is_ongoing"])
        self.assertNotIn("fields", response.data[0])
        self.assertNotIn("starred_by", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"role": "<b></b>"}, "role"),
            ({"started_at": "2026-09-01", "ended_at": "2026-08-01"}, "ended_at"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Changed")
        self.assertEqual(self.project.description, "My website")

        # PATCH tanggal selesai sebelum tanggal mulai yang sudah tersimpan tetap ditolak
        response = self.client.patch(self.detail_url, {"ended_at": "2026-01-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], "visitor")
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True, "is_ongoing": False,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertTrue(response.data["is_ongoing"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        # Grup Editor sudah dibuat oleh migrasi Tugas 4, jadi pakai get_or_create.
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        self.visitor.groups.add(editor_group)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AwardAPITest(APITestCase):
    """API Award (Tugas 6): empat peran Tugas 4, validasi, star, dan CSRF.

    Setiap test penolakan juga memeriksa isi database, bukan hanya status HTTP,
    supaya terbukti datanya benar-benar tidak berubah.
    """

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.user = User.objects.create_user(
            username="biasa", password="test-password", email="biasa@example.com",
        )
        self.editor = User.objects.create_user(username="editor", password="test-password")
        # Grup Editor juga dibuat oleh migrasi Tugas 4, jadi get_or_create aman dipakai.
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        self.editor.groups.add(editor_group)

        self.award = Award.objects.create(
            title="Juara 1 Business Plan", issuer="Universitas Indonesia", year=2025,
            placement="first", level="national", description="Rencana bisnis spirulina",
        )
        self.other_award = Award.objects.create(
            title="Finalis Essay", issuer="ITB", year=2024,
            placement="finalist", level="regional",
        )
        self.list_url = reverse("api:award-list")
        self.detail_url = reverse("api:award-detail", args=[self.award.id])
        self.star_url = reverse("api:award-star", args=[self.award.id])
        self.payload = {
            "title": "Juara 2 LKTI", "issuer": "Universitas Gadjah Mada", "year": 2025,
            "placement": "second", "level": "national", "description": "Karya tulis",
            "certificate_url": "", "is_featured": False,
        }

    def assert_award_unchanged(self):
        self.assertEqual(Award.objects.count(), 2)
        self.award.refresh_from_db()
        self.assertEqual(self.award.title, "Juara 1 Business Plan")

    # --- Membaca data -------------------------------------------------------

    def test_guest_can_read_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        item = next(row for row in response.data if row["id"] == str(self.award.id))
        self.assertEqual(item["placement_display"], "Juara 1")
        self.assertEqual(item["level_display"], "Nasional")
        self.assertFalse(item["is_starred"])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_response_hides_sensitive_account_data(self):
        self.award.starred_by.add(self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.data["starred_by_names"], "biasa")
        self.assertNotIn("starred_by", response.data)
        body = response.content.decode()
        self.assertNotIn("biasa@example.com", body)
        self.assertNotIn("pbkdf2", body)

    def test_search_filter_and_starred_parameters(self):
        response = self.client.get(self.list_url, {"q": "universitas"})
        self.assertEqual([row["id"] for row in response.data], [str(self.award.id)])
        response = self.client.get(self.list_url, {"level": "regional"})
        self.assertEqual([row["id"] for row in response.data], [str(self.other_award.id)])
        # Tingkat yang tidak dikenal diabaikan, bukan menghasilkan error
        self.assertEqual(len(self.client.get(self.list_url, {"level": "galaxy"}).data), 2)
        self.assertEqual(self.client.get(self.list_url, {"q": "tidak-ada"}).data, [])

        self.award.starred_by.add(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"starred": "1"})
        self.assertEqual([row["id"] for row in response.data], [str(self.award.id)])

    def test_missing_award_returns_404(self):
        url = reverse("api:award-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_404_NOT_FOUND)
        star_url = reverse("api:award-star", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(star_url).status_code, status.HTTP_404_NOT_FOUND)

    # --- Empat peran --------------------------------------------------------

    def test_guest_and_regular_user_cannot_write(self):
        for account in (None, self.user):
            self.client.force_authenticate(user=account)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Diubah"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assert_award_unchanged()

    def test_editor_can_patch_and_put(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"title": "Judul Baru"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.award.refresh_from_db()
        self.assertEqual(self.award.title, "Judul Baru")
        self.assertEqual(self.award.issuer, "Universitas Indonesia")  # field lain tidak berubah

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.award.refresh_from_db()
        self.assertEqual(self.award.title, "Juara 2 LKTI")

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assert_award_unchanged()

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Award.objects.get(pk=response.data["id"])
        self.assertEqual(created.issuer, "Universitas Gadjah Mada")

        response = self.client.patch(self.detail_url, {"is_featured": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.award.refresh_from_db()
        self.assertTrue(self.award.is_featured)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Award.objects.filter(pk=self.award.id).exists())

    # --- Validasi -----------------------------------------------------------

    def test_invalid_input_returns_400_and_saves_nothing(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"issuer": "<b></b>"}, "issuer"),
            ({"year": 2999}, "year"),
            ({"year": 1990}, "year"),
            ({"level": "galaxy"}, "level"),
            ({"certificate_url": "javascript:alert(1)"}, "certificate_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, changes)
            self.assertIn(field, response.data)
        self.assertEqual(Award.objects.count(), 2)

    def test_html_tags_are_stripped_from_text(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload,
            "title": "<b>Juara 2</b> LKTI",
            "description": "<script>alert(1)</script>Seru",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Award.objects.get(pk=response.data["id"])
        self.assertEqual(created.title, "Juara 2 LKTI")
        self.assertNotIn("<script>", created.description)

    def test_editor_patch_is_validated_too(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"title": "<i></i>"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_award_unchanged()

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "palsu", "starred_by": [self.user.id],
            "placement_display": "Palsu",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertEqual(response.data["placement_display"], "Juara 2")
        self.assertFalse(Award.objects.get(pk=response.data["id"]).starred_by.exists())

    # --- Star ---------------------------------------------------------------

    def test_guest_cannot_star(self):
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.award.starred_by.count(), 0)

    def test_star_toggles_for_request_user_only(self):
        self.client.force_authenticate(user=self.user)
        # Mencoba memberi star atas nama akun lain lewat body diabaikan
        response = self.client.post(self.star_url, {"user": self.owner.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(list(self.award.starred_by.all()), [self.user])

        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(self.award.starred_by.count(), 0)

    def test_star_only_accepts_post(self):
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # --- CSRF ---------------------------------------------------------------

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_award_unchanged()

    def test_star_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="biasa", password="test-password")
        self.assertEqual(client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.award.starred_by.count(), 0)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="editor", password="test-password")
        # Halaman Award menyetel cookie csrftoken, sama seperti saat dibuka di browser
        client.get(reverse("main:show_award"))
        token = client.cookies["csrftoken"].value
        response = client.patch(
            self.detail_url, {"title": "Lewat Sesi"}, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.award.refresh_from_db()
        self.assertEqual(self.award.title, "Lewat Sesi")
