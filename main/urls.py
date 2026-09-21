from django.urls import path

from main.views import (
    create_award, create_project, delete_award, delete_project,
    get_award_json_by_id, get_awards_json, get_experiences_json,
    get_project_json_by_id, get_projects_json,
    show_award, show_experience, show_main, show_project,
    update_award, update_project,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),

    path("project/", show_project, name="show_project"),
    path("project/add/", create_project, name="create_project"),
    path("project/<uuid:project_id>/edit/", update_project, name="update_project"),
    path("project/<uuid:project_id>/delete/", delete_project, name="delete_project"),

    path("award/", show_award, name="show_award"),
    path("award/add/", create_award, name="create_award"),
    path("award/<uuid:award_id>/edit/", update_award, name="update_award"),
    path("award/<uuid:award_id>/delete/", delete_award, name="delete_award"),

    path("api/experiences/", get_experiences_json, name="get_experiences_json"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("api/projects/<uuid:project_id>/", get_project_json_by_id, name="get_project_json_by_id"),
    path("api/awards/", get_awards_json, name="get_awards_json"),
    path("api/awards/<uuid:award_id>/", get_award_json_by_id, name="get_award_json_by_id"),
]
