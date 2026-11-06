# Legacy OrderHub - Proyecto Base de Modernización y Mantenimiento

> **Asignatura:** Actualización y Mantenimiento de Software  
> **Estado del Sistema:** v2.0 — Django + DRF (arquitectura hexagonal), contenerizado y desplegable en Kubernetes  
> **Cobertura de pruebas:** mínimo 80 % exigido por el CI (`coverage report --fail-under=80`)  

---

## Descripción del Proyecto

**Legacy OrderHub** es una aplicación monolítica encargada de la gestión básica de usuarios, catálogo de productos y procesamiento de órdenes de compra. El sistema fue desarrollado de manera acelerada años atrás para responder a una necesidad puntual de negocio, pero con el tiempo ha acumulado un nivel crítico de **deuda técnica, vulnerabilidades de seguridad y rigidez en la arquitectura**.

Actualmente, el sistema presenta fallas de rendimiento ante picos de tráfico, no cuenta con un entorno de ejecución estandarizado (sin contenerizar), carece de telemetría u observabilidad y las actualizaciones de código se realizan mediante despliegues manuales propensos a errores humanos.

Tu rol como ingeniero/a en este curso será asumir el mantenimiento de este sistema, auditarlo, estabilizarlo y aplicar técnicas modernas (Refactorización manual y asistida por IA, DevOps, Contenerización, SRE y CI/CD) para transformarlo progresivamente en una **aplicación nativa de la nube (Cloud-Native) v2.0**.

---

## Objetivos del Proyecto

### Objetivo General
Evolucionar y modernizar la aplicación **Legacy OrderHub** desde su estado monolítico vulnerable hasta una arquitectura escalable, segura, observadamente monitoreada y desplegada mediante flujos automatizados de CI/CD.

### Objetivos Específicos por Unidad

1. **Unidad I: Modernización Inteligente e Ingeniería Inversa**
   * Realizar auditorías de código estático y dinámico para mapear la deuda técnica y las vulnerabilidades críticas.
   * Refactorizar la arquitectura monolítica aplicando patrones de diseño (*Repository Pattern*, *Dependency Injection*) y asistencia de IA (Copilotos/Agentes).
   * Eliminar vulnerabilidades de seguridad de alto impacto (SQL Injection, exposición de secretos, contraseñas en texto plano).

2. **Unidad II: DevOps 2.0 y Calidad Automatizada**
   * Automatizar el flujo de integración continua (CI) mediante GitHub Actions / GitLab CI.
   * Implementar puertas de calidad (*Quality Gates*) para prevenir la entrada de nuevo código defectuoso.
   * Asignar métricas cuantitativas al costo de la deuda técnica y estimación de refactorización.

3. **Unidad III: Contenerización, IaC y SRE**
   * Empaquetar la aplicación y sus dependencias utilizando contenedores Docker.
   * Definir y desplegar la infraestructura en Kubernetes configurando autoescalado horizontal (HPA).
   * Gestionar secretos y variables de entorno de forma segura e independiente del código.

4. **Unidad IV: Despliegue Progresivo y Observabilidad**
   * Instrumentar la aplicación para generación de logs estructurados, métricas de rendimiento y trazas distribuidas.
   * Implementar estrategias de despliegue sin caída de servicio (*Blue/Green* o *Canary*).
   * Automatizar pruebas de regresión y de carga asistidas por IA para validar paridad funcional y resiliencia.

---

## Stack Tecnológico Actual vs. Estado Objetivo

| Componente | Estado Actual (v1.0 - Legado) | Estado Objetivo (v2.0 - Modernizado) |
| :--- | :--- | :--- |
| **Lenguaje / Framework** | Python 3.8 / Flask Monolítico | Python 3.12+ / Django + Django REST Framework (Arquitectura Hexagonal) |
| **Base de Datos** | SQLite (Sin migraciones / SQL Directo) | PostgreSQL + Django ORM y migraciones (SQLite en desarrollo local) |
| **Seguridad** | Secretos *hardcoded*, contraseñas plano | `.env` / Vault, Hash Bcrypt/Argon2, JWT |
| **Pruebas** | Ninguna (0% coverage) | `manage.py test` + coverage >= 80 % |
| **Infraestructura** | Ejecución local/servidor directo | Docker Compose + Kubernetes (Minikube/k3s) |
| **CI / CD** | Despliegue manual | GitHub Actions / GitLab CI + SonarQube |
| **Observabilidad** | `print()` en consola | Logs JSON + `/metrics` (Prometheus) + dashboard Grafana (RED) |

---

## Módulos y Puntos Críticos Detectados (Deuda Técnica)

A continuación se resumen las áreas más críticas identificadas en el sistema actual que deberán ser abordadas durante el curso:

* **Vulnerabilidades de Seguridad:** Inyección de SQL en el endpoint `/login`, almacenamiento de credenciales en texto plano y credenciales de base de datos expuestas en el repositorio (`config.py`).
* **Código Acoplado (Spaghetti):** El endpoint `/create_order` mezcla control de HTTP, lógica de cálculo de negocio, transacciones a la base de datos y llamadas sincrónicas a servicios externos.
* **Falta de Manejo de Errores y Transacciones:** Fallos en la red o llamadas externas dejan la base de datos en estados inconsistentes (p. ej., stock descontado sin notificación confirmada).
* **Configuración Rígida:** Modo `debug=True` activado por defecto y puertos quemados en el código.

---

## Guía de Inicio Rápido (Django)

## La API estará disponible en http://localhost:8000.

### Reglas del Proyecto Durante el Curso

1. Prohibido hacer Push directo a la rama main: Todas las modificaciones deben realizarse mediante ramas (Feature Branches) y ser integradas a través de Pull Requests.

2. Cero Tolerancia a Secretos: No se aceptará ningún commit que contenga claves, tokens o contraseñas en texto plano.

3. Documentación Continua: Cada refactorización o cambio arquitectónico importante debe quedar documentado en la carpeta /docs.

¡Bienvenido/a al proceso de modernización! El éxito de la operación depende de tu capacidad para diagnosticar, refactorizar y automatizar.

### Requisitos Previos
* Python 3.12 o superior instalado.
* Git.

### Pasos para Ejecutar
1. Clonar este repositorio:
   ```bash
   git clone [https://github.com/tu-usuario/legacy-orderhub.git](https://github.com/tu-usuario/legacy-orderhub.git)
   cd legacy-orderhub
   ```
2. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   # En Linux/macOS:
   source venv/bin/activate
   # En Windows:
   venv\Scripts\activate
   ```
3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Copiar `.env.example` a `.env` (y generar un `DJANGO_SECRET_KEY` propio si vas a desplegar):
   ```bash
   cp .env.example .env
   ```
5. Aplicar las migraciones (crea la base de datos SQLite y siembra los datos iniciales):
   ```bash
   python manage.py migrate
   ```
6. Levantar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```
7. Ejecutar las pruebas:
   ```bash
   python manage.py test
   ```


---

## Despliegue y operación

### Docker Compose (API + PostgreSQL + Redis)
```bash
cp .env.example .env        # defina DJANGO_SECRET_KEY y POSTGRES_PASSWORD
docker compose up --build   # API en http://localhost:8000
```

### Kubernetes (Minikube / k3s)
Manifiestos en [`k8s/`](k8s/README.md): Deployment, Service, ConfigMap, Secret, HPA (2–5 réplicas al 70 % CPU),
PostgreSQL, Redis y Job de migraciones. Monitoreo (Prometheus + Grafana) en `k8s/monitoring/`.
Despliegue Canary 90/10 con rollback automático en `k8s/canary/`.

### Pruebas de carga
Script de Locust en [`loadtest/`](loadtest/README.md).

### Endpoints operativos
`/healthcheck` (liveness/readiness) y `/metrics` (Prometheus).

### Documentación
[`docs/ANALYSIS_AND_REQUIREMENTS.md`](docs/ANALYSIS_AND_REQUIREMENTS.md) ·
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) ·
[`docs/HEXAGONAL_ARCHITECTURE.md`](docs/HEXAGONAL_ARCHITECTURE.md) ·
[`docs/TECHNICAL_DEBT_LOG.md`](docs/TECHNICAL_DEBT_LOG.md)

### Despliegue en Render (CI/CD)
- **CI** (`.github/workflows/ci.yml`): en cada push a `main` o `Dev` y en cada Pull Request a `main` ejecuta estilo, SAST, pruebas con cobertura >= 80 %, build de la imagen con prueba de humo contra PostgreSQL y validacion de manifiestos de Kubernetes.
- **CD** (`.github/workflows/cd.yml`): solo se ejecuta cuando el CI termina correctamente sobre `main`. En un unico job dispara el despliegue en Render mediante un Deploy Hook, espera a que `/healthcheck` informe el commit desplegado y ejecuta pruebas de humo en produccion.
- Secretos de GitHub necesarios: `RENDER_DEPLOY_HOOK_URL` y `RENDER_SERVICE_URL`.
- Base de datos: PostgreSQL en Supabase (`DATABASE_URL` en las variables de entorno de Render).
- Contrasenas iniciales de `admin` y `juan`: variables `SEED_ADMIN_PASSWORD` y `SEED_USER_PASSWORD` (solo se aplican cuando la tabla de usuarios esta vacia).
