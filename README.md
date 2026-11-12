# Address Book API

A REST API for managing addresses and finding the ones within a given distance of a location.

Built with **FastAPI, SQLAlchemy, Pydantic and SQLite**.

## Features

- Create, read, update (full or partial) and delete addresses.
- Each address stores its coordinates (latitude and longitude).
- Input validation, including coordinate ranges.
- Find addresses within a distance (km) of a point, nearest first.
- Pagination on the list endpoint, a health check, and automated tests.
- Logging to the console and to a log file that rotates.

## Project Structure

```
address-book-api/
├── app/
│   ├── main.py                  # App factory, startup, router registration
│   ├── api/
│   │   ├── health.py            # / and /health
│   │   └── v1/
│   │       ├── router.py
│   │       └── addresses.py     # Address endpoints
│   ├── core/
│   │   ├── config.py            # Settings from environment / .env
│   │   ├── exceptions.py
│   │   ├── exception_handlers.py
│   │   └── logging.py           # Console and rotating file logging
│   ├── db/
│   │   ├── base.py
│   │   └── session.py           # Engine, session, get_db dependency
│   ├── models/
│   │   └── address.py           # SQLAlchemy model
│   ├── schemas/
│   │   └── address.py           # Request/response schemas
│   ├── services/
│   │   └── address_service.py   # Business logic and DB queries
│   └── utils/
│       └── geo.py               # Haversine distance
├── tests/                       # Endpoint, schema, geo, nearby and logging tests
├── logs/                        # Created on startup (not in git)
├── .env.example
├── pytest.ini
└── requirements.txt
```

Routes only handle HTTP, the service layer holds the logic and queries, and the schemas validate input and shape output.

## Setup

Requires Python 3.10 or newer (tested with 3.13).

```
git clone https://github.com/aishwaryapatle/Address-Book-API.git
cd Address-Book-API
```

Create and activate a virtual environment:

```
# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:

```
pip install -r requirements.txt
```

No configuration is needed. To change the defaults (database path, debug logging, log file), copy `.env.example` to `.env` and edit it.

## Run the App

From the project root:

```
python -m uvicorn app.main:app --reload
```

| Resource   | URL                           |
| ---------- | ----------------------------- |
| Swagger UI | http://127.0.0.1:8000/docs    |
| ReDoc      | http://127.0.0.1:8000/redoc   |

The SQLite file `address_book.db` and its table are created automatically on startup. Swagger UI is the easiest way to try every endpoint.

## API

| Method | Endpoint                         | Description                              |
| ------ | -------------------------------- | ---------------------------------------- |
| GET    | `/`                              | Welcome message                          |
| GET    | `/health`                        | Database health check                    |
| POST   | `/api/v1/addresses`              | Create an address                        |
| GET    | `/api/v1/addresses`              | List addresses (`skip`, `limit`)         |
| GET    | `/api/v1/addresses/{id}`         | Get an address                           |
| PUT    | `/api/v1/addresses/{id}`         | Replace an address (send all fields)     |
| PATCH  | `/api/v1/addresses/{id}`         | Update one or more fields                |
| DELETE | `/api/v1/addresses/{id}`         | Delete an address                        |
| GET    | `/api/v1/addresses/nearby`       | Find addresses within a distance         |

### Address fields

| Field         | Rules                              |
| ------------- | ---------------------------------- |
| `name`        | Required, up to 100 characters     |
| `street`      | Required, up to 255 characters     |
| `city`        | Required, up to 100 characters     |
| `state`       | Required, up to 100 characters     |
| `country`     | Required, up to 100 characters     |
| `postal_code` | Required, up to 20 characters      |
| `latitude`    | Required, between -90 and 90       |
| `longitude`   | Required, between -180 and 180     |

Text is trimmed, and blank values are rejected. `PUT` needs all of these fields. `PATCH` accepts any of them, needs at least one, and does not allow `null`.

### Example: create an address

Shown with `curl` (macOS, Linux or Git Bash). On Windows you can use Swagger UI instead.

```
curl -X POST http://127.0.0.1:8000/api/v1/addresses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Office",
    "street": "Civil Lines",
    "city": "Nagpur",
    "state": "Maharashtra",
    "country": "India",
    "postal_code": "440001",
    "latitude": 21.1458,
    "longitude": 79.0882
  }'
```

Response (`201 Created`):

```json
{
  "name": "Office",
  "street": "Civil Lines",
  "city": "Nagpur",
  "state": "Maharashtra",
  "country": "India",
  "postal_code": "440001",
  "latitude": 21.1458,
  "longitude": 79.0882,
  "id": 1,
  "created_at": "2026-11-11T12:00:00Z",
  "updated_at": "2026-11-11T12:00:00Z"
}
```

### Example: find nearby addresses

```
curl "http://127.0.0.1:8000/api/v1/addresses/nearby?latitude=21.1458&longitude=79.0882&distance_km=5"
```

| Parameter     | Description                                   |
| ------------- | --------------------------------------------- |
| `latitude`    | Search point latitude (-90 to 90)             |
| `longitude`   | Search point longitude (-180 to 180)          |
| `distance_km` | Search radius in km, greater than 0           |
| `limit`       | Max results returned (default 20, max 100)    |

Response (`200 OK`):

```json
{
  "search_location": { "latitude": 21.1458, "longitude": 79.0882 },
  "distance_km": 5.0,
  "total": 1,
  "items": [
    {
      "name": "Office",
      "street": "Civil Lines",
      "city": "Nagpur",
      "state": "Maharashtra",
      "country": "India",
      "postal_code": "440001",
      "latitude": 21.1458,
      "longitude": 79.0882,
      "id": 1,
      "created_at": "2026-11-11T12:00:00Z",
      "updated_at": "2026-11-11T12:00:00Z",
      "distance_km": 0.0
    }
  ]
}
```

`total` is the number of matches within the radius, even if `limit` returns fewer. Results are sorted by distance, and an address exactly on the boundary is included.

### Status codes

| Code  | Meaning                                  |
| ----- | ---------------------------------------- |
| `200` | Success                                  |
| `201` | Address created                          |
| `204` | Address deleted                          |
| `404` | Address not found                        |
| `422` | Validation failed                        |
| `500` | Database or unexpected error (logged)    |

Errors look like `{"detail": "Address with ID 99 not found"}`. Validation errors (422) use FastAPI's default format.

## How Nearby Search Works

The distance between two points is calculated with the **Haversine formula**, which accounts for the curvature of the Earth:

```
a = sin²(Δlat / 2) + cos(lat1) · cos(lat2) · sin²(Δlon / 2)
c = 2 · atan2(√a, √(1 − a))
distance = R · c          (R = 6371 km, angles in radians)
```

To avoid calculating the distance for every row, a SQL query first keeps only addresses inside the matching latitude band. The exact Haversine check is then done in Python on those rows. This is fine for an address book; for very large datasets a spatial index (SpatiaLite or PostGIS) would be the next step.

## Logging

Logs go to the console and to `logs/app.log`. The file rotates: when it reaches 5 MB it is renamed to `app.log.1` and a new file starts. The 3 most recent old files are kept. The folder is created on startup and is not part of git.

What is logged:

- `INFO`: the app starting and stopping, and addresses being created, updated or deleted.
- `WARNING`: requests for an address that does not exist (404).
- `ERROR`: database errors and any unexpected error, with the full traceback.

The file path can be changed with `LOG_FILE` in `.env`. Set `DEBUG=True` to also log debug messages.

## Run the Tests

```
python -m pytest
```

The tests use an in-memory SQLite database, so your `address_book.db` is not touched. They cover the CRUD endpoints, validation, pagination, nearby search and the distance calculation.

## Notes

- Timestamps are stored in UTC.
- Tables are created with `create_all` on startup. There are no migrations; Alembic would be the next step if the schema starts changing.
- Possible improvements: Docker, authentication, and a spatial index for nearby search.
