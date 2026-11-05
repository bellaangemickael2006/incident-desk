"""Search helper for the local synthetic exercise — ORM-based, owner-scoped."""
from incidents.models import Incident

def search_incidents(user_id, query):
    # Fixed: query structure is defined by the ORM; user input is bound as a
    # parameterised value and can never alter the WHERE owner clause.
    qs = Incident.objects.filter(created_by_id=user_id)
    if query:
        qs = qs.filter(title__icontains=query)
    return list(
        qs.order_by("-created_at")[:20]
        .values("id", "title", "description")
    )
