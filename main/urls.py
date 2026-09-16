from django.urls import path

from main.views import (
    show_main, show_experience, show_project, show_award,
    create_project, get_projects_json, delete_project
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("project/", show_project, name="show_project"),
    path("project/add/", create_project, name="create_project"),
    path("award/", show_award, name="show_award"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("project/<uuid:project_id>/delete/", delete_project, name="delete_project"),
]