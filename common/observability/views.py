import os

from django.db import connection
from django.http import JsonResponse


def healthcheck(request):
    # RENDER_GIT_COMMIT lo define Render; permite al CD verificar que la version
    # desplegada es la esperada.
    version = os.environ.get("RENDER_GIT_COMMIT", "dev")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse(
            {"status": "error", "database": "down", "version": version}, status=503
        )
    return JsonResponse({"status": "ok", "database": "up", "version": version})
