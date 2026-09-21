import uuid
from datetime import date

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
        Project.objects.create(
            title="Sistem Informasi Akademik",
            description="Membangun sistem akademik berbasis web.",
            role="Full Stack Developer",
            started_at=timezone.now().date(),
        )
        response = self.client.get(reverse("main:show_project"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, "Sistem Informasi Akademik")
        self.assertContains(response, "Membangun sistem akademik")
        self.assertContains(response, "Full Stack Developer")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_project_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_project"))
        self.assertContains(response, "Belum ada proyek yang ditambahkan.")

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
