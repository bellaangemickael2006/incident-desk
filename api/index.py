from config.environment import prepare_environment
prepare_environment()

import django
django.setup()

# Run pending DB migrations on cold start (idempotent, required for axes tables).
from django.core.management import call_command
try:
    call_command("migrate", "--noinput", verbosity=0)
except Exception:
    pass  # App still serves; check Vercel logs if auth fails.

from config.wsgi import application

__all__ = ["application"]
