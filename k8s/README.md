# Despliegue en Kubernetes (HU-07)

Requisitos: Minikube/k3s con `metrics-server` (`minikube addons enable metrics-server`).

```bash
docker build -t legacy-order-hub:latest .
minikube image load legacy-order-hub:latest
# Edite secret.yaml (o cree el Secret con kubectl, ver comentario) y luego:
kubectl apply -k k8s/
kubectl -n orderhub get pods,hpa
minikube service orderhub -n orderhub --url
```

- `Deployment`: 2 réplicas, no root, probes liveness/readiness en `/healthcheck`.
- `HPA`: 2–5 réplicas al superar 70 % de CPU.
- `Service`: NodePort 30080 → puerto 8000.
- PostgreSQL corre como `StatefulSet` con volumen persistente.

## Monitoreo (RNF-05)

```bash
kubectl apply -k k8s/monitoring/
minikube service grafana -n orderhub --url   # usuario: admin
```

Prometheus descubre los pods con la anotación `prometheus.io/scrape` y añade la etiqueta
`version` (stable/canary). Grafana carga el dashboard "OrderHub - Métricas RED" automáticamente.
Para `canary_check.sh`: `kubectl -n orderhub port-forward svc/prometheus 9090:9090`.

## Redis y migraciones
- `redis.yaml`: Redis 7. La app publica cada orden creada en el stream `orderhub:order_created` (`REDIS_URL`).
- `migrate-job.yaml`: aplica las migraciones una sola vez; los pods web usan `RUN_MIGRATIONS=false`.
  Si lo re-aplica, borre antes el Job (`kubectl -n orderhub delete job orderhub-migrate`), porque su plantilla es inmutable.
