import uuid
from datetime import date

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.forms import AwardForm, ProjectForm
from main.models import Experience, Project, Award


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_project_model(self):
        project = Project.objects.create(
            title="Sistem Informasi Akademik",
            description="Membangun sistem akademik berbasis web.",
            role="Full Stack Developer",
            started_at=timezone.now().date(),
        )
        self.assertEqual(str(project), "Sistem Informasi Akademik")
        self.assertEqual(project.role, "Full Stack Developer")
        self.assertTrue(project.is_ongoing)

    def test_project_page(self):
        """Halaman project hanya berisi kerangka. Datanya diambil browser dari endpoint JSON."""
        Project.objects.create(
            title="Sistem Informasi Akademik",
            description="Membangun sistem akademik berbasis web.",
            role="Full Stack Developer",
            started_at=timezone.now().date(),
        )
        response = self.client.get(reverse("main:show_project"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, 'id="grid"')
        self.assertContains(response, reverse("main:get_projects_json"))
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertNotContains(response, "Sistem Informasi Akademik")

        fields = self.client.get(reverse("main:get_projects_json")).json()[0]["fields"]
        self.assertEqual(fields["title"], "Sistem Informasi Akademik")
        self.assertEqual(fields["role"], "Full Stack Developer")
        self.assertTrue(fields["is_ongoing"])

    def test_empty_project_page(self):
        Project.objects.all().delete()
        self.assertEqual(self.client.get(reverse("main:get_projects_json")).json(), [])

    def test_award_model(self):
        award = Award.objects.create(
            title="1st Place Data Science",
            issuer="Universitas Indonesia",
            year=2024
        )
        self.assertEqual(str(award), "1st Place Data Science")
        self.assertEqual(award.issuer, "Universitas Indonesia")

    def test_award_page(self):
        Award.objects.create(
            title="1st Place Data Science",
            issuer="Universitas Indonesia",
            year=2024
        )
        response = self.client.get(reverse("main:show_award"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "award.html")
        self.assertContains(response, "1st Place Data Science")
        self.assertContains(response, "Universitas Indonesia")
        self.assertContains(response, "2024")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_award_page(self):
        Award.objects.all().delete()
        response = self.client.get(reverse("main:show_award"))
        self.assertContains(response, "Belum ada penghargaan yang ditambahkan.")

class AwardCrudTest(TestCase):
    """Tes alur form & data delivery untuk bagian Award (Tugas 3)."""

    def setUp(self):
        self.award = Award.objects.create(
            title="1st Place Business Plan",
            issuer="Universitas Indonesia",
            year=2024,
            placement="first",
            level="national",
        )
        owner = User.objects.create_superuser("pemilik", password="Pemilik-Test-123")
        self.client.force_login(owner)
        self.valid_data = {
            "title": "Finalist Hackathon",
            "issuer": "Fasilkom UI",
            "year": 2025,
            "placement": "finalist",
            "level": "internal",
            "description": "Membuat aplikasi antrean klinik.",
            "certificate_url": "https://example.com/sertifikat",
            "is_featured": "on",
        }

    def test_award_form_excludes_auto_fields(self):
        fields = AwardForm().fields
        for auto_field in ("id", "created_at", "updated_at"):
            self.assertNotIn(auto_field, fields)
        self.assertGreaterEqual(len(fields), 3)

    def test_award_form_rejects_future_year(self):
        data = {**self.valid_data, "year": timezone.now().year + 1}
        form = AwardForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("year", form.errors)

    def test_create_award_page(self):
        response = self.client.get(reverse("main:create_award"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "award_form.html")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_create_award(self):
        response = self.client.post(reverse("main:create_award"), self.valid_data, follow=True)
        self.assertRedirects(response, reverse("main:show_award"))
        award = Award.objects.get(title="Finalist Hackathon")
        self.assertTrue(award.is_featured)
        self.assertContains(response, "berhasil ditambahkan")

    def test_create_award_invalid_data_stays_on_form(self):
        response = self.client.post(reverse("main:create_award"), {"title": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Award.objects.count(), 1)

    def test_update_award_page_is_prefilled(self):
        response = self.client.get(reverse("main:update_award", args=[self.award.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="1st Place Business Plan"')

    def test_update_award(self):
        data = {**self.valid_data, "title": "1st Place Business Plan (Revisi)"}
        response = self.client.post(reverse("main:update_award", args=[self.award.id]), data)
        self.assertRedirects(response, reverse("main:show_award"))
        self.award.refresh_from_db()
        self.assertEqual(self.award.title, "1st Place Business Plan (Revisi)")
        self.assertEqual(Award.objects.count(), 1)

    def test_update_unknown_award_returns_404(self):
        response = self.client.get(reverse("main:update_award", args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, 404)

    def test_delete_award_requires_post(self):
        response = self.client.get(reverse("main:delete_award", args=[self.award.id]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Award.objects.filter(pk=self.award.pk).exists())

    def test_delete_award(self):
        response = self.client.post(reverse("main:delete_award", args=[self.award.id]))
        self.assertRedirects(response, reverse("main:show_award"))
        self.assertFalse(Award.objects.filter(pk=self.award.pk).exists())

    def test_awards_json(self):
        response = self.client.get(reverse("main:get_awards_json"))
        self.assertEqual(response["Content-Type"], "application/json")
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["title"], "1st Place Business Plan")

    def test_awards_json_filters(self):
        Award.objects.create(title="Best Paper", issuer="IEEE", year=2025, level="international")
        by_level = self.client.get(reverse("main:get_awards_json"), {"level": "international"}).json()
        self.assertEqual([item["fields"]["title"] for item in by_level], ["Best Paper"])
        by_query = self.client.get(reverse("main:get_awards_json"), {"q": "indonesia"}).json()
        self.assertEqual([item["fields"]["title"] for item in by_query], ["1st Place Business Plan"])

    def test_unknown_level_filter_falls_back_to_all(self):
        response = self.client.get(reverse("main:show_award"), {"level": "hacker"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_level"], "")
        self.assertContains(response, "1st Place Business Plan")

    def test_award_json_by_id(self):
        response = self.client.get(reverse("main:get_award_json_by_id", args=[self.award.id]))
        self.assertEqual(response.json()[0]["pk"], str(self.award.id))

    def test_award_page_renders_deserialized_json(self):
        response = self.client.get(reverse("main:show_award"))
        self.assertContains(response, "1st Place Business Plan")
        self.assertContains(response, "Universitas Indonesia")
        self.assertContains(response, "2024")
        self.assertContains(response, reverse("main:update_award", args=[self.award.id]))
        self.assertContains(response, reverse("main:delete_award", args=[self.award.id]))


class ProjectUpdateAndJsonTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Portfolio Website",
            description="Website portofolio pribadi.",
            role="Fullstack Developer",
            started_at=date(2026, 8, 1),
        )
        owner = User.objects.create_superuser("pemilik", password="Pemilik-Test-123")
        self.client.force_login(owner)

    def test_update_project(self):
        data = {
            "title": "Portfolio Website v2",
            "description": "Website portofolio pribadi.",
            "role": "Fullstack Developer",
            "started_at": "2026-08-01",
            "ended_at": "2026-09-21",
        }
        response = self.client.post(reverse("main:update_project", args=[self.project.id]), data)
        self.assertRedirects(response, reverse("main:show_project"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio Website v2")
        self.assertFalse(self.project.is_ongoing)

    def test_project_end_date_before_start_is_rejected(self):
        form = ProjectForm(data={
            "title": "X", "description": "Y", "role": "Z",
            "started_at": "2026-08-01", "ended_at": "2026-07-01",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("ended_at", form.errors)

    def test_project_json_by_id(self):
        response = self.client.get(reverse("main:get_project_json_by_id", args=[self.project.id]))
        self.assertEqual(response.json()[0]["fields"]["title"], "Portfolio Website")

    def test_experiences_json(self):
        Experience.objects.create(title="Asdos PBP", description="Membantu tutorial.")
        response = self.client.get(reverse("main:get_experiences_json"))
        self.assertEqual(response.json()[0]["fields"]["title"], "Asdos PBP")


class RoleAccessTest(TestCase):
    """Tes hak akses keempat peran pada bagian Award (Tugas 4)."""

    def setUp(self):
        self.award = Award.objects.create(title="Juara Hackathon", issuer="Fasilkom UI", year=2025)
        self.user = User.objects.create_user("biasa", password="Biasa-Test-123")
        self.editor = User.objects.create_user("editor", password="Editor-Test-123")
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.owner = User.objects.create_superuser("pemilik", password="Pemilik-Test-123")
        self.create_url = reverse("main:create_award")
        self.update_url = reverse("main:update_award", args=[self.award.id])
        self.delete_url = reverse("main:delete_award", args=[self.award.id])
        self.star_url = reverse("main:toggle_award_star", args=[self.award.id])

    def test_editor_group_is_created_by_migration(self):
        self.assertTrue(Group.objects.filter(name="Editor").exists())

    def test_visitor_is_redirected_to_login(self):
        for url in (self.create_url, self.update_url):
            response = self.client.get(url)
            self.assertRedirects(response, f"/login/?next={url}", fetch_redirect_response=False)
        for url in (self.delete_url, self.star_url):
            response = self.client.post(url)
            self.assertRedirects(response, f"/login/?next={url}", fetch_redirect_response=False)

    def test_visitor_can_read(self):
        response = self.client.get(reverse("main:show_award"))
        self.assertContains(response, "Juara Hackathon")
        self.assertNotContains(response, self.update_url)
        self.assertNotContains(response, self.delete_url)
        self.assertNotContains(response, self.create_url)

    def test_regular_user_gets_403_on_changes(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.create_url).status_code, 403)
        self.assertEqual(self.client.get(self.update_url).status_code, 403)
        self.assertEqual(self.client.post(self.delete_url).status_code, 403)
        self.assertTrue(Award.objects.filter(pk=self.award.pk).exists())

    def test_editor_can_update_but_not_create_or_delete(self):
        self.client.force_login(self.editor)
        self.assertEqual(self.client.get(self.update_url).status_code, 200)
        self.assertEqual(self.client.get(self.create_url).status_code, 403)
        self.assertEqual(self.client.post(self.delete_url).status_code, 403)

        response = self.client.get(reverse("main:show_award"))
        self.assertContains(response, self.update_url)
        self.assertNotContains(response, self.delete_url)
        self.assertNotContains(response, self.create_url)

    def test_owner_sees_all_controls(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("main:show_award"))
        self.assertContains(response, self.create_url)
        self.assertContains(response, self.update_url)
        self.assertContains(response, self.delete_url)

    def test_star_toggles_once_per_user(self):
        self.client.force_login(self.user)
        self.client.post(self.star_url)
        self.assertEqual(self.award.starred_by.count(), 1)
        response = self.client.get(reverse("main:show_award"))
        self.assertContains(response, "Unstar")

        self.client.post(self.star_url)
        self.assertEqual(self.award.starred_by.count(), 0)

    def test_star_requires_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)

    def test_awards_json_shows_username_not_user_id(self):
        self.award.starred_by.add(self.user)
        fields = self.client.get(reverse("main:get_awards_json")).json()[0]["fields"]
        self.assertEqual(fields["starred_by"], [["biasa"]])
        self.assertNotIn("password", str(fields))


class ProjectAjaxTest(TestCase):
    """Tes endpoint AJAX halaman Project (Tutorial 5)."""

    def setUp(self):
        self.project = Project.objects.create(
            title="Portfolio Website",
            description="Website portofolio pribadi.",
            role="Fullstack Developer",
            started_at=date(2026, 8, 1),
        )
        self.user = User.objects.create_user("biasa", password="Biasa-Test-123")
        self.owner = User.objects.create_superuser("pemilik", password="Pemilik-Test-123")
        self.list_url = reverse("main:get_projects_json")
        self.create_url = reverse("main:create_project_ajax")
        self.valid_data = {
            "title": "Aplikasi Kasir",
            "description": "Aplikasi kasir sederhana.",
            "role": "Backend Developer",
            "started_at": "2026-09-01",
        }

    def test_projects_json_includes_star_info(self):
        self.project.starred_by.add(self.user)

        fields = self.client.get(self.list_url).json()[0]["fields"]
        self.assertEqual(fields["star_count"], 1)
        self.assertEqual(fields["starred_by_names"], "biasa")
        self.assertFalse(fields["is_starred"])
        self.assertNotIn("password", str(fields))

        self.client.force_login(self.user)
        fields = self.client.get(self.list_url).json()[0]["fields"]
        self.assertTrue(fields["is_starred"])

    def test_projects_json_filters_by_title(self):
        self.assertEqual(len(self.client.get(self.list_url, {"title": "portfolio"}).json()), 1)
        self.assertEqual(self.client.get(self.list_url, {"title": "tidak ada"}).json(), [])

    def test_modal_only_for_owner(self):
        page_url = reverse("main:show_project")
        self.assertNotContains(self.client.get(page_url), 'id="add-project-modal"')
        self.client.force_login(self.owner)
        self.assertContains(self.client.get(page_url), 'id="add-project-modal"')

    def test_create_ajax_requires_post(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.create_url).status_code, 405)

    def test_create_ajax_rejects_visitor_and_regular_user_with_json(self):
        response = self.client.post(self.create_url, self.valid_data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("message", response.json())

        self.client.force_login(self.user)
        self.assertEqual(self.client.post(self.create_url, self.valid_data).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_create_ajax_by_owner(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.create_url, self.valid_data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(pk=response.json()["pk"], title="Aplikasi Kasir").exists())

    def test_create_ajax_invalid_data_returns_errors(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.create_url, {**self.valid_data, "title": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])

    def test_form_strips_html_tags(self):
        form = ProjectForm(data={**self.valid_data, "title": "Halo <b>dunia</b>"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], "Halo dunia")

    def test_form_rejects_title_with_only_html(self):
        self.client.force_login(self.owner)
        payload = {**self.valid_data, "title": '<img src="x" onerror="alert(1)">'}
        response = self.client.post(self.create_url, payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])
