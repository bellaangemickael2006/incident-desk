from django.urls import path
from .views import (
    IncidentAnalystUpdateView, IncidentCreateView,
    IncidentDeleteView, IncidentDetailView, IncidentListView,
)

app_name = "incidents"
urlpatterns = [
    path("incidents/", IncidentListView.as_view(), name="list"),
    path("incidents/new/", IncidentCreateView.as_view(), name="create"),
    path("incidents/<int:pk>/", IncidentDetailView.as_view(), name="detail"),
    path("incidents/<int:pk>/update/", IncidentAnalystUpdateView.as_view(), name="update"),
    path("incidents/<int:pk>/delete/", IncidentDeleteView.as_view(), name="delete"),
]
