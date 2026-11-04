# Guía de presentación — Legacy OrderHub (sin tecnicismos)

## 1. El proyecto en 30 segundos
Legacy OrderHub gestiona usuarios, productos y órdenes de compra. Lo recibimos **viejo y con problemas serios**
(Flask, contraseñas en texto plano, vulnerable a inyección SQL, sin pruebas, sin automatización).
Lo **modernizamos** a Django con una arquitectura ordenada por capas, segura, probada, empaquetada en
contenedores y lista para correr en Kubernetes con monitoreo.

## 2. Antes y después

| Problema del sistema viejo | Qué hicimos | Evidencia |
|---|---|---|
| Inyección SQL en `/login` | Consultas por ORM; el ataque `' OR '1'='1` devuelve 401 | Prueba automática y prueba manual |
| Contraseñas en texto plano | Hash Argon2 y sesión con token JWT que expira | Login funciona; BD sin claves legibles |
| Secretos en el código | Todo en variables de entorno (`.env`, ignorado por git) | `bandit` sin hallazgos |
| Código mezclado (spaghetti) | Capas: dominio, aplicación, infraestructura, API | `docs/HEXAGONAL_ARCHITECTURE.md` |
| Sin pruebas | 43 pruebas, **93 % de cobertura** (mínimo exigido: 80 %) | `coverage report` |
| Despliegue manual | CI en GitHub Actions: estilo, seguridad, pruebas, build de Docker | Pestaña Actions del repositorio |
| Corre "en mi máquina" | Docker + Docker Compose (app + PostgreSQL + Redis) | Probado en Codespaces |
| No escala | Kubernetes con autoescalado de 2 a 5 réplicas | Captura del HPA: CPU 176 %, 2 → 5 réplicas |
| Sin visibilidad | Logs en JSON, endpoint `/metrics`, dashboard Grafana | `/metrics` y dashboard |

## 3. Demo en vivo (5 minutos, en tu computador)
Terminal 1 (con `(.venv)` activo): `python manage.py runserver`

1. Abre http://localhost:8000 → el panel. Usuario `juan`, contraseña `123456` → **Iniciar sesión**.
2. Pulsa **Cargar Órdenes**. (Para que haya datos, crea una orden antes con la terminal o con el admin.)
3. http://localhost:8000/healthcheck → `{"status": "ok"}`: "así Kubernetes sabe si la app está viva".
4. http://localhost:8000/metrics → "así Prometheus mide la app: peticiones, errores y latencia".
5. En la terminal del servidor se ve el log en JSON de cada orden creada ("notificación asíncrona").
6. Muestra las pruebas: `python manage.py test` → `Ran 43 tests ... OK`.

## 4. Capturas que debes llevar
- Cola del HPA con la CPU sobre 70 % y las réplicas pasando de 2 a 5.
- `kubectl -n orderhub get pods` con todos en `Running` y el Job de migraciones en `Completed`.
- `docker compose ps` con los 3 servicios `healthy` y `whoami` → `appuser` (no corre como administrador).
- Redis con el evento de la orden (`XRANGE orderhub:order_created - +`).
- El Pull Request con el CI en verde (cuando lo tengas).
- Grafana con el dashboard, si alcanzas a mostrarlo.

## 5. Preguntas probables
- **¿Por qué Docker?** Para que la app corra igual en cualquier computador, sin "en mi máquina sí funciona".
- **¿Qué es Kubernetes?** Un administrador de contenedores: los reinicia si fallan y crea copias si sube el tráfico.
- **¿Qué es el HPA?** La regla que sube de 2 a 5 copias de la app cuando la CPU pasa del 70 %.
- **¿Por qué Redis?** Para publicar un evento por cada orden sin hacer esperar al usuario.
- **¿Qué es el CI?** Un robot en GitHub que revisa estilo, seguridad y pruebas en cada cambio antes de aceptarlo.
- **¿Qué es el canary?** Mandar el 10 % del tráfico a una versión nueva y volver atrás sola si falla.

## 6. Qué decir de lo que no se alcanzó (con honestidad)
Las piezas de Grafana, el despliegue canary con rollback y la publicación en un servicio en la nube
están **escritas y versionadas** (`k8s/monitoring`, `k8s/canary`), pero si no se alcanzaron a ejecutar,
dilo así: "implementadas, falta la verificación en el clúster". Decir lo que está probado y lo que no
suma credibilidad.
