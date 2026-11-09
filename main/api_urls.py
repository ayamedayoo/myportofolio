from django.urls import path

from main import api_views

app_name = "api"

urlpatterns = [
    path("projects/", api_views.project_list, name="project-list"),
    path("projects/<uuid:project_id>/", api_views.project_detail, name="project-detail"),
    path("projects/<uuid:project_id>/star/", api_views.project_star, name="project-star"),

    path("awards/", api_views.award_list, name="award-list"),
    path("awards/<uuid:award_id>/", api_views.award_detail, name="award-detail"),
    path("awards/<uuid:award_id>/star/", api_views.award_star, name="award-star"),
]
