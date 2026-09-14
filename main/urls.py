from django.urls import path

from main.views import show_main, show_experience, show_project, show_award

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("project/", show_project, name="show_project"),
    path("award/", show_award, name="show_award"),
]