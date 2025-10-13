# Quantum Fleet Core — Documentación Técnica (ES)
**Versión del código**: instantánea del repositorio proporcionado  
**Fecha**: 2025-10-13

> Esta guía documenta **cada componente** del proyecto, su **arquitectura**, **instalación**, **configuración**, **modelo de datos**, **API** y **servicios** de ingesta. Está pensada para desarrolladores y operadores (DevOps).

## 1) Descripción general
Plataforma de backend para **gestión e ingesta de telemetría** multi‑tenant basada en **FastAPI + PostgreSQL**, con soporte para:
- **Ingesta HTTP** firmada por *token de dispositivo*.
- **Ingesta por MQTT** (EMQX) mediante un *worker* que reenvía a la API.
- **Ingesta Teltonika** (FMC650): servidor TCP + *collector* HTTP.
- **RBAC multi‑tenant** (roles: `admin`, `manager`, `viewer`).
- **Dashboards y panels** persistidos por tenant.
- **Conectores HTTP** (salientes) y **webhooks** (entrantes) gestionados por API.

## 2) Estructura del repositorio
```
├── .env
├── backend
│
 
 
 
├
─
─
 
D
o
c
k
e
r
f
i
l
e


│
 
 
 
├
─
─
 
a
l
e
m
b
i
c


│


 


 


 


│


 


 


 


├


─


─


 


e


n


v


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


s


c


r


i


p


t


.


p


y


.


m


a


k


o






│


 


 


 


│


 


 


 


└


─


─


 


v


e


r


s


i


o


n


s






│






 






 






 






│






 






 






 






 






 






 






 






├






─






─






 






0






0






0






1






_






i






n






i






t






.






p






y














│






 






 






 






│






 






 






 






 






 






 






 






├






─






─






 






0






0






0






2






_






r






b






a






c






.






p






y














│






 






 






 






│






 






 






 






 






 






 






 






├






─






─






 






0






0






0






3






_






f






k






_






c






a






s






c






a






d






e






.






p






y














│






 






 






 






│






 






 






 






 






 






 






 






├






─






─






 






0






0






0






4






_






d






a






s






h






b






o






a






r






d






s






.






p






y














│






 






 






 






│






 






 






 






 






 






 






 






├






─






─






 






1






3






7






e






7






c






e






1






a






0






6






2






_






m






e






r






g






e






_






h






e






a






d






s






.






p






y














│






 






 






 






│






 






 






 






 






 






 






 






├






─






─






 






2






0






2






5






1






0






0






3






_






a






d






d






_






t






e






l






e






m






e






t






r






y






_






i






n






d






e






x






e






s






.






p






y














│






 






 






 






│






 






 






 






 






 






 






 






├






─






─






 






2






0






2






5






1






0






0






7






_






b






o






o






t






s






t






r






a






p






_






d






e






v






i






c






e






s






_






t






e






l






e






m






e






t






r






y






.






p






y














│






 






 






 






│






 






 






 






 






 






 






 






└






─






─






 






e






0






1






d






7






2






6






6






9






d






a






a






_






m






e






r






g






e






_






h






e






a






d






s






.






p






y


│
 
 
 
├
─
─
 
a
l
e
m
b
i
c
.
i
n
i


│
 
 
 
├
─
─
 
a
p
p


│


 


 


 


│


 


 


 


├


─


─


 


_


_


i


n


i


t


_


_


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


_


_


p


y


c


a


c


h


e


_


_






│






 






 






 






│






 






 






 






│






 






 






 






└






─






─






 






_






_






i






n






i






t






_






_






.






c






p






y






t






h






o






n






-






3






1






0






.






p






y






c






│


 


 


 


│


 


 


 


├


─


─


 


a


u


t


h


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


c


o


n


f


i


g


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


d


a


t


a


b


a


s


e


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


d


e


p


s


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


i


n


t


e


g


r


a


t


i


o


n


s






│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






_






_






i






n






i






t






_






_






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






└






─






─






 






t






e






l






t






o






n






i






k






a






_






f






m






c






6






5






0






.






p






y






│


 


 


 


│


 


 


 


├


─


─


 


m


a


i


n


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


m


o


d


e


l


s


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


m


o


d


e


l


s


_


d


a


s


h


b


o


a


r


d


s


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


m


o


d


e


l


s


_


r


b


a


c


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


p


a


r


s


e


r


s






│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






_






_






i






n






i






t






_






_






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






_






_






p






y






c






a






c






h






e






_






_














│














 














 














 














│














 














 














 














│














 














 














 














│














 














 














 














└














─














─














 














_














_














i














n














i














t














_














_














.














c














p














y














t














h














o














n














-














3














1














0














.














p














y














c














│






 






 






 






│






 






 






 






│






 






 






 






└






─






─






 






t






e






l






t






o






n






i






k






a














│














 














 














 














│














 














 














 














│














 














 














 














 














 














 














 














├














─














─














 














_














_














i














n














i














t














_














_














.














p














y






























│














 














 














 














│














 














 














 














│














 














 














 














 














 














 














 














├














─














─














 














_














_














p














y














c














a














c














h














e














_














_






























│






























 






























 






























 






























│






























 






























 






























 






























│






























 






























 






























 






























 






























 






























 






























 






























│






























 






























 






























 






























├






























─






























─






























 






























_






























_






























i






























n






























i






























t






























_






























_






























.






























c






























p






























y






























t






























h






























o






























n






























-






























3






























1






























0






























.






























p






























y






























c






























































│






























 






























 






























 






























│






























 






























 






























 






























│






























 






























 






























 






























 






























 






























 






























 






























│






























 






























 






























 






























└






























─






























─






























 






























f






























m






























c






























6






























5






























0






























.






























c






























p






























y






























t






























h






























o






























n






























-






























3






























1






























0






























.






























p






























y






























c






























│














 














 














 














│














 














 














 














│














 














 














 














 














 














 














 














├














─














─














 














f














m














c














6














5














0














.














p














y






























│














 














 














 














│














 














 














 














│














 














 














 














 














 














 














 














├














─














─














 














i














d














s














_














f














m














c














6














5














0














_














m














i














n














.














j














s














o














n






























│














 














 














 














│














 














 














 














│














 














 














 














 














 














 














 














└














─














─














 














t














e














l














t














o














n














i














k














a














_














F














M














C














6














5














0














.














p














y






│


 


 


 


│


 


 


 


├


─


─


 


r


o


u


t


e


r


s






│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






_






_






i






n






i






t






_






_






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






a






d






m






i






n






_






r






o






l






e






s






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






a






u






d






i






t






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






c






o






n






n






e






c






t






o






r






s






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






d






a






s






h






b






o






a






r






d






s






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






d






e






v






i






c






e






s






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






i






n






g






e






s






t






_






h






t






t






p






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






i






n






g






e






s






t






_






t






e






l






t






o






n






i






k






a






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






t






e






l






e






m






e






t






r






y






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






t






e






l






e






m






e






t






r






y






_






r






e






a






d






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






├






─






─






 






t






e






n






a






n






t






s






.






p






y














│






 






 






 






│






 






 






 






│






 






 






 






└






─






─






 






u






s






e






r






s






.






p






y






│


 


 


 


│


 


 


 


├


─


─


 


s


c


h


e


m


a


s


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


s


c


h


e


m


a


s


_


d


a


s


h


b


o


a


r


d


s


.


p


y






│


 


 


 


│


 


 


 


├


─


─


 


s


c


h


e


m


a


s


_


r


b


a


c


.


p


y






│


 


 


 


│


 


 


 


└


─


─


 


u


t


i


l


s






│






 






 






 






│






 






 






 






 






 






 






 






├






─






─






 






_






_






i






n






i






t






_






_






.






p






y














│






 






 






 






│






 






 






 






 






 






 






 






├






─






─






 






r






b






a






c






.






p






y














│






 






 






 






│






 






 






 






 






 






 






 






└






─






─






 






s






e






c






u






r






i






t






y






.






p






y


│
 
 
 
├
─
─
 
p
y
t
e
s
t
.
i
n
i


│
 
 
 
├
─
─
 
r
e
q
u
i
r
e
m
e
n
t
s
-
d
e
v
.
t
x
t


│
 
 
 
├
─
─
 
r
e
q
u
i
r
e
m
e
n
t
s
.
t
x
t


│
 
 
 
└
─
─
 
t
e
s
t
s


│


 


 


 


 


 


 


 


├


─


─


 


c


o


n


f


t


e


s


t


.


p


y






│


 


 


 


 


 


 


 


├


─


─


 


t


e


s


t


_


i


n


g


e


s


t


_


e


n


d


p


o


i


n


t


.


p


y






│


 


 


 


 


 


 


 


└


─


─


 


t


e


s


t


_


t


e


l


t


o


n


i


k


a


_


f


m


c


6


5


0


.


p


y
├── docker-compose.yml
├── scripts
│
 
 
 
├
─
─
 
c
l
e
a
n
_
d
e
v
i
c
e
s
.
s
h


│
 
 
 
└
─
─
 
d
e
m
o
_
d
a
s
h
b
o
a
r
d
s
.
s
h
├── services
│
 
 
 
├
─
─
 
e
x
t
e
r
n
a
l
-
c
o
l
l
e
c
t
o
r


│


 


 


 


│


 


 


 


├


─


─


 


D


o


c


k


e


r


f


i


l


e






│


 


 


 


│


 


 


 


├


─


─


 


c


o


l


l


e


c


t


o


r


.


p


y






│


 


 


 


│


 


 


 


└


─


─


 


r


e


q


u


i


r


e


m


e


n


t


s


.


t


x


t


│
 
 
 
├
─
─
 
m
q
t
t
-
w
o
r
k
e
r


│


 


 


 


│


 


 


 


├


─


─


 


D


o


c


k


e


r


f


i


l


e






│


 


 


 


│


 


 


 


├


─


─


 


r


e


q


u


i


r


e


m


e


n


t


s


.


t


x


t






│


 


 


 


│


 


 


 


└


─


─


 


w


o


r


k


e


r


.


p


y


│
 
 
 
└
─
─
 
t
e
l
t
o
n
i
k
a
-
t
c
p


│


 


 


 


 


 


 


 


├


─


─


 


D


o


c


k


e


r


f


i


l


e






│


 


 


 


 


 


 


 


├


─


─


 


r


e


q


u


i


r


e


m


e


n


t


s


.


t


x


t






│


 


 


 


 


 


 


 


├


─


─


 


s


e


r


v


e


r


.


p


y






│


 


 


 


 


 


 


 


└


─


─


 


s


e


r


v


e


r


.


p


y


.


b


a


k
└── tools
 
 
 
 
├
─
─
 
d
e
m
o
_
c
o
n
n
e
c
t
o
r
s
.
s
h


 
 
 
 
├
─
─
 
d
e
m
o
_
p
o
s
t
_
j
s
o
n
.
s
h


 
 
 
 
├
─
─
 
s
i
m
_
f
m
c
6
5
0
.
p
y


 
 
 
 
├
─
─
 
s
m
o
k
e
_
c
o
n
n
e
c
t
o
r
_
w
e
b
h
o
o
k
.
s
h


 
 
 
 
└
─
─
 
s
m
o
k
e
_
t
e
l
t
o
n
i
k
a
.
s
h
```


## 3) Arquitectura y componentes

### 3.1 Backend API (FastAPI)
- Ubicación: `backend/app` (arranque con Uvicorn).
- Endpoints montados en `app.main` y routers en `backend/app/routers`.
- Autenticación: **JWT** (issuance en `/auth/login`), `OAuth2PasswordBearer`.
- CORS permisivo en desarrollo (restringir en producción).
- Migraciones: **Alembic** (`backend/alembic`).

### 3.2 Base de datos (PostgreSQL)
- Tablas principales: connector_logs, connectors, dashboard_panels, dashboards, devices, saved_queries, telemetry, tenants, user_roles, users.
- Índices: `ix_telemetry_tenant_device_ts` (+ migraciones 2025-10-03 / 2025-10-07).
- Esquema gestionado por modelos SQLAlchemy y/o DDL específicos en algunos routers (p.ej. `connectors`).

### 3.3 Broker MQTT (EMQX) y worker
- Servicio **emqx** (puerto 1883 por defecto).
- Servicio **mqtt-worker** (`services/mqtt-worker/worker.py`) suscrito a `ingest/+`.  
  Mensaje → POST a `/ingest/http`.  
```bash
# Publica en MQTT (EMQX) en el tópico 'ingest/<TOKEN>'
# payload puede ser {"data": {...}, "ts": "..."} o directamente {"k":"v"} (se toma como data)
mosquitto_pub -h localhost -p 1883 -t "ingest/TOKEN_DEL_DISPOSITIVO" -m '{"gps":{"lat":-33.4,"lon":-70.6}}'
```


### 3.4 Ingesta Teltonika
- **Servidor TCP** (`services/teltonika-tcp/server.py`) escucha en `${TCP_PORT}` (por defecto 5072), maneja handshake IMEI y decodifica **AVL**.
- **Collector HTTP** (`services/external-collector/collector.py`) lee de *sources* y reenvía a `/ingest/teltonika/ingest`.  
  - Transforms soportados: `round`, `clamp` sobre campos.
- **Parser FMC650** (`backend/app/integrations/teltonika_fmc650.py` y `backend/app/parsers/teltonika/*`).

Simulación rápida de FMC650:
```bash
# Simula un FMC650 enviando 3 tramas AVL al servidor TCP
python3 tools/sim_fmc650.py --host 127.0.0.1 --port 5072 --imei 356307042123456 --count 3   --lat -33.41 --lon -70.61 --speed 18.5
```


### 3.5 Conectores y Webhooks
- Gestión de **conectores** vía `/connectors` con almacenamiento en `public.connectors` y logs en `public.connector_logs`.
- **Webhook** entrante: `/hooks/{token}`.
- **Llamada saliente**: `/connectors/{id}/call`.

### 3.6 Dashboards
- Entidades: `dashboards`, `dashboard_panels`, `saved_queries` (JSONB).
- CRUD completo con prefijo `/tenants/{tenant_id}/dashboards`.

## 4) Instalación y arranque (local con Docker)
1. **Prerrequisitos**: Docker, Docker Compose, `make` (opcional).
2. **Variables**: copia `.env` y ajusta valores (ver sección 5). **NUNCA** reutilices secretos de ejemplo en prod.
3. **Arranque**:
```bash
docker compose up -d
```

4. **Migraciones** (dentro del contenedor `api`):
```bash
docker compose exec api alembic upgrade head
```

5. **Smoke tests**:
   - Healthcheck:
```bash
curl -s http://localhost:8000/health
```

   - Teltonika ping:
```bash
curl -s http://localhost:8000/ingest/teltonika/ping
```

   - Demo dashboards:
```bash
bash scripts/demo_dashboards.sh
```


## 5) Configuración (.env)
Ajusta estos parámetros. Los valores de ejemplo se muestran **enmascarados**:
- **SECRET_KEY** = `2e…db`
- **ACCESS_TOKEN_EXPIRE_MINUTES** = `***`
- **POSTGRES_DB** = `qu…et`
- **POSTGRES_USER** = `qu…um`
- **POSTGRES_PASSWORD** = `qu…23`
- **DATABASE_URL** = `po…et`
- **JWT_SECRET** = `su…me`
- **JWT_ALG** = `***`
- **JWT_EXPIRE_MINUTES** = `***`
- **EMQX_HOST** = `***`
- **EMQX_PORT** = `***`
- **EMQX_PASSWORD** = `Si…$$`
- **MQTT_USERNAME** = `io…er`
- **MQTT_PASSWORD** = `In…5!`
- **API_HOST** = `0.….0`
- **API_PORT** = `***`
- **TCP_BIND** = `0.….0`
- **TCP_PORT** = `***`
- **VITE_API_BASE** = `http://***`

### Notas
- `DATABASE_URL` usa driver SQLAlchemy `postgresql+psycopg`.
- `JWT_SECRET`, `SECRET_KEY`, credenciales de DB y EMQX deben **rotarse** en producción.
- `VITE_API_BASE` se usa por el frontend (si aplica) para CORS/URLs.
- `TCP_PORT` define el puerto del servidor Teltonika TCP.

## 6) Modelo de datos (resumen)
- **tenants**: organizaciones. (`id`, `name`, `slug`)
- **users**: credenciales básicas (`email`, `password_hash`, `role`, `tenant_id`).
- **user_roles**: RBAC por tenant (`user_id`, `tenant_id`, `role` ∈ {admin,manager,viewer}).
- **devices**: dispositivos con `token` y `external_id` únicos (FK a `tenants`).
- **telemetry**: puntos `{ts, data(JSON)}` con índices por `tenant_id`, `device_id`, `ts`.
- **dashboards / dashboard_panels / saved_queries**: configuración de UI y queries (JSONB).
- **connectors / connector_logs**: metadatos de conectores y bitácora de llamadas.

## 7) Seguridad y RBAC
- Autenticación: **JWT** emitido en `/auth/login` (OAuth2 password flow).
- Autorización: dependencias `require_role(RoleEnum.…)` y helper `get_tenant_id()` (cabecera `X-Tenant-Id` o path `{tenant_id}`).
- Prioridad de roles: `viewer < manager < admin`.
- CORS abierto en dev → **restringir dominios en PROD**.

## 8) API REST (catálogo)
A continuación, todos los endpoints detectados automáticamente desde los *routers* de FastAPI:
### auth

- **POST** `/auth/login` (función `login` en `users.py`)
- **POST** `/auth/register` (función `register` en `users.py`)

### connectors

- **GET** `/connectors` (función `list_connectors` en `connectors.py`)
- **POST** `/connectors` (función `create_or_update_connector` en `connectors.py`)
- **POST** `/connectors/{connector_id}/call` (función `call_connector` en `connectors.py`)
- **POST** `/hooks/{token}` (función `webhook_receiver` en `connectors.py`)

### dashboards

- **GET** `/tenants/{tenant_id}/dashboards` (función `list_dashboards` en `dashboards.py`)
- **POST** `/tenants/{tenant_id}/dashboards` (función `create_dashboard` en `dashboards.py`)
- **DELETE** `/tenants/{tenant_id}/dashboards/{dashboard_id}` (función `delete_dashboard` en `dashboards.py`)
- **GET** `/tenants/{tenant_id}/dashboards/{dashboard_id}` (función `get_dashboard` en `dashboards.py`)
- **PATCH** `/tenants/{tenant_id}/dashboards/{dashboard_id}` (función `update_dashboard_patch` en `dashboards.py`)
- **PUT** `/tenants/{tenant_id}/dashboards/{dashboard_id}` (función `update_dashboard_put` en `dashboards.py`)
- **POST** `/tenants/{tenant_id}/dashboards/{dashboard_id}/panels` (función `create_panel` en `dashboards.py`)
- **DELETE** `/tenants/{tenant_id}/dashboards/{dashboard_id}/panels/{panel_id}` (función `delete_panel` en `dashboards.py`)
- **GET** `/tenants/{tenant_id}/dashboards/{dashboard_id}/panels/{panel_id}` (función `get_panel` en `dashboards.py`)
- **PATCH** `/tenants/{tenant_id}/dashboards/{dashboard_id}/panels/{panel_id}` (función `update_panel_patch` en `dashboards.py`)
- **PUT** `/tenants/{tenant_id}/dashboards/{dashboard_id}/panels/{panel_id}` (función `update_panel_put` en `dashboards.py`)

### devices

- **GET** `/devices` (función `list_devices` en `devices.py`)
- **POST** `/devices` (función `create_device` en `devices.py`)
- **DELETE** `/devices/{device_id}` (función `delete_device` en `devices.py`)
- **PATCH** `/devices/{device_id}` (función `patch_device` en `devices.py`)
- **PUT** `/devices/{device_id}` (función `put_device` en `devices.py`)

### ingest

- **POST** `/ingest/http` (función `ingest_http` en `ingest_http.py`)

### ingest: teltonika

- **POST** `/ingest/teltonika/ingest` (función `ingest_one` en `ingest_teltonika.py`)
- **GET** `/ingest/teltonika/ping` (función `ping` en `ingest_teltonika.py`)

### roles

- **GET** `/tenants/{tenant_id}/users/{user_id}/roles` (función `list_roles_for_user` en `admin_roles.py`)
- **POST** `/tenants/{tenant_id}/users/{user_id}/roles/{role}` (función `set_role` en `admin_roles.py`)

### telemetry

- **GET** `/telemetry/query` (función `get_telemetry` en `telemetry_read.py`)
- **POST** `/telemetry/query` (función `query_telemetry` en `telemetry.py`) — Devuelve la telemetría más reciente para un device del tenant del usuario,
con filtros de tiempo opcionales.

### tenants

- **GET** `/tenants` (función `list_tenants` en `tenants.py`)
- **POST** `/tenants` (función `create_tenant` en `tenants.py`)

### untagged

- **GET** `/audit/events` (función `list_audit_events` en `audit.py`) — Lista eventos con filtros opcionales.
NOTA: `ip::text` para que Pydantic reciba string (evita IPv4Address).
- **POST** `/audit/events` (función `create_audit_event` en `audit.py`) — Inserta un evento de auditoría y, como side-effect:
  - device.connected: abre sesión de dispositivo (cierra previas abiertas).
  - device.keepalive/device.message: refresca last_seen.
  - device.disconnected: cierra sesión abierta.
  - user.login: abre sesión de usuario (sin depender de public.users).
  - user.keepalive: refresca last_seen.
  - user.logout: cierra sesión abierta.


### Ejemplos rápidos
**Login (JWT):**
```bash
curl -s -X POST "http://localhost:8000/auth/login"   -H "Content-Type: application/x-www-form-urlencoded"   --data "username=admin@example.com&password=Admin123!"
```


**Ingesta HTTP directa:**
```bash
curl -s -X POST "http://localhost:8000/ingest/http"   -H "Content-Type: application/json"   -d '{
    "token": "TOKEN_DEL_DISPOSITIVO",
    "ts": "2025-01-01T12:00:00Z",
    "data": {"gps":{"lat":-33.4,"lon":-70.6,"speed":12.3},"io":{"24":65,"239":1}}
  }'
```


**Consulta de telemetría (POST):**
```bash
curl -s -X POST "http://localhost:8000/telemetry/query"   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"device_id": 1, "limit": 100}'
```


## 9) Servicios en docker-compose
Servicios detectados:
- **api**
- **emqx**
- **external-collector**
- **mqtt-worker**
- **pgdata**
- **postgres**
- **redis**
- **teltonika-tcp**

Arrancan con `docker compose up -d`. Revisa *logs* con `docker compose logs -f <servicio>`.

## 10) Flujo de datos (alto nivel)
1. **Dispositivo → EMQX (MQTT)**: publica en `ingest/<token>` → **mqtt-worker** → `POST /ingest/http` → **DB (telemetry)**.
2. **Dispositivo Teltonika (TCP)**: FMC650 → **teltonika-tcp** (decodifica AVL) → **external-collector** (normaliza y reenvía) → `POST /ingest/teltonika/ingest` → **DB**.
3. **Webhooks externos**: `POST /hooks/{token}` → reglas/mapping → **connector_logs**.

## 11) Desarrollo y pruebas
- Ejecuta la API local (sin Docker):
```bash

cd backend
uvicorn app.main:app --reload --port 8000
```

- Migraciones:
```bash

cd backend
alembic upgrade head
```

- Tests E2E (opcional, ver `backend/tests/` y variables `E2E`, `API`, `TENANT`):
```bash

E2E=1 API=http://localhost:8000 TENANT=1 pytest -q backend/tests
```


## 12) Buenas prácticas (producción)
- Rotar **JWT_SECRET/SECRET_KEY** y credenciales de DB/EMQX; usar **secrets manager**.
- CORS restringido y `allow_origins` → lista blanca.
- Reforzar índices y *retención* en `telemetry` si el volumen crece.
- Telemetría sensible → encriptación en reposo y tránsito.
- Auditoría: activar persistencia `user_sessions` y revisar `/audit/events`.
- Backups y *health checks* periódicos.
