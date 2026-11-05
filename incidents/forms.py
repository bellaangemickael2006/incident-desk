from django import forms
from .models import Comment, Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        # Ownership, assigned_to, status and initial severity are server-controlled.
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "A short, descriptive title", "autofocus": True}),
            "description": forms.Textarea(attrs={"rows": 8, "placeholder": "What happened? Include synthetic details only."}),
        }
        help_texts = {
            "title": "3–150 characters.",
            "description": "10–5,000 characters. Use plain text; do not enter passwords or personal data.",
            "severity": "Estimated impact level.",
        }


class AnalystIncidentForm(forms.ModelForm):
    """Analysts can update status and assignment; they cannot change ownership."""
    class Meta:
        model = Incident
        fields = ["severity", "status", "assigned_to"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4, "placeholder": "Add a comment…"}),
        }
        help_texts = {
            "content": "Plain text only. Do not include passwords or personal data.",
        }
