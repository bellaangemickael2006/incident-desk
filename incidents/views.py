from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView
from django.views.generic.edit import DeleteView, FormMixin

from .forms import AnalystIncidentForm, CommentForm, IncidentForm
from .models import AuditEvent, Comment, Incident


def _is_analyst_or_admin(user):
    return user.groups.filter(name__in=["analyst", "admin"]).exists() or user.is_staff


class HomeView(TemplateView):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("incidents:list")
        return super().get(request, *args, **kwargs)


class OwnedIncidentsMixin(LoginRequiredMixin):
    def get_queryset(self):
        user = self.request.user
        # Analysts and admins see all incidents; reporters see only their own.
        if _is_analyst_or_admin(user):
            return Incident.objects.select_related("created_by", "assigned_to").all()
        return Incident.objects.filter(created_by=user)


class IncidentListView(OwnedIncidentsMixin, ListView):
    model = Incident
    template_name = "incidents/list.html"
    context_object_name = "incidents"
    paginate_by = 20


class IncidentDetailView(FormMixin, OwnedIncidentsMixin, DetailView):
    model = Incident
    template_name = "incidents/detail.html"
    context_object_name = "incident"
    form_class = CommentForm

    def get_success_url(self):
        return reverse("incidents:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["comment_form"] = self.get_form()
        ctx["comments"] = self.object.comments.select_related("author").all()
        ctx["is_analyst"] = _is_analyst_or_admin(self.request.user)
        if ctx["is_analyst"]:
            ctx["analyst_form"] = AnalystIncidentForm(instance=self.object)
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.incident = self.object
        comment.author = self.request.user
        comment.save()
        AuditEvent.objects.create(
            incident=self.object,
            actor=self.request.user,
            verb="added_comment",
        )
        messages.success(self.request, "Comment added.")
        return super().form_valid(form)


class IncidentCreateView(LoginRequiredMixin, CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = "incidents/form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        AuditEvent.objects.create(
            incident=self.object,
            actor=self.request.user,
            verb="created_incident",
        )
        messages.success(self.request, "Your incident has been recorded.")
        return response

    def get_success_url(self):
        return reverse("incidents:detail", kwargs={"pk": self.object.pk})


class IncidentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Admins (is_staff) can permanently delete an incident."""
    model = Incident
    template_name = "incidents/confirm_delete.html"
    success_url = reverse_lazy("incidents:list")

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Incident.objects.all()

    def form_valid(self, form):
        incident_ref = str(self.object)
        AuditEvent.objects.create(
            incident=self.object,
            actor=self.request.user,
            verb="deleted_incident",
            detail=f"Deleted: {incident_ref}",
        )
        messages.success(self.request, f"{incident_ref} has been deleted.")
        return super().form_valid(form)


class IncidentAnalystUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Analysts and admins can update severity, status and assignment."""
    model = Incident
    form_class = AnalystIncidentForm
    template_name = "incidents/analyst_update.html"

    def test_func(self):
        return _is_analyst_or_admin(self.request.user)

    def form_valid(self, form):
        old = Incident.objects.get(pk=self.object.pk)
        response = super().form_valid(form)
        changes = []
        for field in ["severity", "status", "assigned_to"]:
            old_val = getattr(old, field)
            new_val = getattr(self.object, field)
            if old_val != new_val:
                changes.append(f"{field}: {old_val} → {new_val}")
        if changes:
            AuditEvent.objects.create(
                incident=self.object,
                actor=self.request.user,
                verb="updated_incident",
                detail="; ".join(changes),
            )
        messages.success(self.request, "Incident updated.")
        return response

    def get_success_url(self):
        return reverse("incidents:detail", kwargs={"pk": self.object.pk})
