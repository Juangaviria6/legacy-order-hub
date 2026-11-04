#!/bin/sh
# Valida la tasa de error del canary y hace rollback automático si supera el umbral (HU-09.3).
# Requiere Prometheus accesible (django-prometheus expone django_http_responses_total_by_status_total)
# y que scrapee los pods con la etiqueta "version" (véase anotaciones prometheus.io/* del Deployment).
#
# Uso: PROM_URL=http://localhost:9090 THRESHOLD=0.01 k8s/canary/canary_check.sh
set -eu

PROM_URL="${PROM_URL:-http://localhost:9090}"
THRESHOLD="${THRESHOLD:-0.01}"
NS="${NS:-orderhub}"

query() {
  curl -s --get "$PROM_URL/api/v1/query" --data-urlencode "query=$1" |
    sed -n 's/.*"value":\[[^,]*,"\([^"]*\)"\].*/\1/p'
}

ERRORS=$(query 'sum(rate(django_http_responses_total_by_status_total{version="canary",status=~"5.."}[2m]))')
TOTAL=$(query 'sum(rate(django_http_responses_total_by_status_total{version="canary"}[2m]))')
ERRORS="${ERRORS:-0}"; TOTAL="${TOTAL:-0}"

RATE=$(awk -v e="$ERRORS" -v t="$TOTAL" 'BEGIN { print (t > 0) ? e / t : 0 }')
echo "Tasa de error del canary: $RATE (umbral $THRESHOLD)"

if awk -v r="$RATE" -v th="$THRESHOLD" 'BEGIN { exit !(r > th) }'; then
  echo "Umbral superado: ejecutando rollback del canary"
  kubectl -n "$NS" delete ingress orderhub-canary --ignore-not-found
  kubectl -n "$NS" scale deployment orderhub-canary --replicas=0
  exit 1
fi
echo "Canary saludable"
