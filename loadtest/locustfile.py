"""Pruebas de carga de Legacy OrderHub (HU-09).

Uso:
    pip install locust
    locust -f loadtest/locustfile.py --host http://localhost:8000 \
        --headless -u 50 -r 10 -t 2m

Credenciales por variables de entorno (no se versionan secretos).
El login se hace una sola vez y el token se reutiliza: hashear con Argon2 es
costoso en CPU y memoria, y no es lo que se quiere medir aquí.
"""

import os

from gevent.lock import Semaphore
from locust import HttpUser, between, task

_token_lock = Semaphore()
_token = {"value": ""}


class OrderHubUser(HttpUser):
    wait_time = between(0.5, 2)

    def on_start(self):
        with _token_lock:
            if not _token["value"]:
                response = self.client.post(
                    "/login",
                    json={
                        "username": os.environ.get("LOAD_USER", "juan"),
                        "password": os.environ.get("LOAD_PASSWORD", ""),
                    },
                )
                if response.ok:
                    _token["value"] = response.json().get("access", "")
        self.client.headers["Authorization"] = f"Bearer {_token['value']}"

    @task(5)
    def list_products(self):
        self.client.get("/products")

    @task(2)
    def list_orders(self):
        self.client.get("/get_all_orders_legacy")

    @task(2)
    def create_order(self):
        self.client.post("/create_order", json={"product_id": 2, "quantity": 1})

    @task(1)
    def healthcheck(self):
        self.client.get("/healthcheck")
