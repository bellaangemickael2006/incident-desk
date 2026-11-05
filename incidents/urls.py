from django.urls import path
from .views import (
    IncidentAnalystUpdateView, IncidentCreateView,
    IncidentDetailView, IncidentListView,
)

app_name = "incidents"
urlpatterns = [
    path("", IncidentListView.as_view(), name="list"),
    path("incidents/new/", IncidentCreateView.as_view(), name="create"),
    path("incidents/<int:pk>/", IncidentDetailView.as_view(), name="detail"),
    path("incidents/<int:pk>/update/", IncidentAnalystUpdateView.as_view(), name="update"),
]
