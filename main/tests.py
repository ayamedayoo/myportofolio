from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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