
from datetime import datetime


def test_create_address(client, sample_address):
    response = client.post(
        "/api/v1/addresses",
        json=sample_address,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Home"
    assert data["city"] == "Pune"
    assert data["latitude"] == 18.5204
    assert "created_at" in data
    assert "updated_at" in data


def test_list_addresses(client, sample_address):
    client.post("/api/v1/addresses", json=sample_address)

    response = client.get("/api/v1/addresses")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Home"


def test_list_addresses_pagination(client, sample_address):
    for index in range(3):
        address = sample_address.copy()
        address["name"] = f"Address {index + 1}"

        client.post("/api/v1/addresses", json=address)

    response = client.get(
        "/api/v1/addresses",
        params={"skip": 1, "limit": 1},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Address 2"


def test_get_address_by_id(client, sample_address):
    create_response = client.post(
        "/api/v1/addresses",
        json=sample_address,
    )

    address_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/addresses/{address_id}"
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Home"


def test_get_nonexistent_address(client):
    response = client.get("/api/v1/addresses/999")

    assert response.status_code == 404


def test_non_positive_address_id_is_rejected(client):
    zero_response = client.get("/api/v1/addresses/0")
    negative_response = client.get("/api/v1/addresses/-1")

    assert zero_response.status_code == 422
    assert negative_response.status_code == 422


def test_update_address(client, sample_address):
    create_response = client.post(
        "/api/v1/addresses",
        json=sample_address,
    )

    address_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/addresses/{address_id}",
        json={"city": "Mumbai"},
    )

    assert response.status_code == 200
    assert response.json()["city"] == "Mumbai"
    assert response.json()["name"] == "Home"


def test_update_nonexistent_address(client):
    response = client.patch(
        "/api/v1/addresses/999",
        json={"city": "Mumbai"},
    )

    assert response.status_code == 404


def test_delete_address(client, sample_address):
    create_response = client.post(
        "/api/v1/addresses",
        json=sample_address,
    )

    address_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/addresses/{address_id}"
    )

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(
        f"/api/v1/addresses/{address_id}"
    )

    assert get_response.status_code == 404


def test_delete_nonexistent_address(client):
    response = client.delete("/api/v1/addresses/999")

    assert response.status_code == 404


def test_create_address_with_invalid_latitude(
    client,
    sample_address,
):
    sample_address["latitude"] = 95

    response = client.post(
        "/api/v1/addresses",
        json=sample_address,
    )

    assert response.status_code == 422


def test_create_address_with_invalid_longitude(
    client,
    sample_address,
):
    sample_address["longitude"] = 200

    response = client.post(
        "/api/v1/addresses",
        json=sample_address,
    )

    assert response.status_code == 422


def test_empty_patch_is_rejected(client, sample_address):
    create_response = client.post(
        "/api/v1/addresses",
        json=sample_address,
    )

    address_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/addresses/{address_id}",
        json={},
    )

    assert response.status_code == 422


def test_null_patch_field_is_rejected(client, sample_address):
    create_response = client.post(
        "/api/v1/addresses",
        json=sample_address,
    )

    address_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/addresses/{address_id}",
        json={"city": None},
    )

    assert response.status_code == 422


def test_update_changes_timestamp(client, sample_address):
    create_response = client.post(
        "/api/v1/addresses",
        json=sample_address,
    )

    created = create_response.json()

    response = client.patch(
        f"/api/v1/addresses/{created['id']}",
        json={"city": "Mumbai"},
    )

    updated = response.json()

    assert response.status_code == 200
    assert datetime.fromisoformat(updated["updated_at"]) >= datetime.fromisoformat(
        created["updated_at"]
    )
    assert datetime.fromisoformat(updated["updated_at"]) >= datetime.fromisoformat(
        created["created_at"]
    )


def test_invalid_pagination_parameters(client):
    skip_response = client.get(
        "/api/v1/addresses",
        params={"skip": -1},
    )
    limit_response = client.get(
        "/api/v1/addresses",
        params={"limit": 0},
    )
    large_limit_response = client.get(
        "/api/v1/addresses",
        params={"limit": 101},
    )

    assert skip_response.status_code == 422
    assert limit_response.status_code == 422
    assert large_limit_response.status_code == 422


def test_whitespace_only_city_is_rejected(client, sample_address):
    sample_address["city"] = "   "

    response = client.post(
        "/api/v1/addresses",
        json=sample_address,
    )

    assert response.status_code == 422


def test_list_response_includes_page_bounds(client):
    response = client.get(
        "/api/v1/addresses",
        params={"skip": 0, "limit": 20},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["skip"] == 0
    assert data["limit"] == 20


def test_empty_address_list(client):
    response = client.get("/api/v1/addresses")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["items"] == []


def test_timestamps_are_utc_on_create_and_get(client, db_session, sample_address):
    created = client.post("/api/v1/addresses", json=sample_address).json()

    # Force a real read from SQLite, which returns naive datetimes.
    db_session.expire_all()
    fetched = client.get(f"/api/v1/addresses/{created['id']}").json()

    for body in (created, fetched):
        assert datetime.fromisoformat(body["created_at"]).utcoffset() is not None


def test_put_replaces_all_fields(client, sample_address):
    created = client.post("/api/v1/addresses", json=sample_address).json()

    new_data = sample_address.copy()
    new_data["name"] = "Office"
    new_data["city"] = "Mumbai"

    response = client.put(f"/api/v1/addresses/{created['id']}", json=new_data)

    assert response.status_code == 200
    assert response.json()["name"] == "Office"
    assert response.json()["city"] == "Mumbai"


def test_put_requires_all_fields(client, sample_address):
    created = client.post("/api/v1/addresses", json=sample_address).json()

    response = client.put(
        f"/api/v1/addresses/{created['id']}",
        json={"city": "Mumbai"},
    )

    assert response.status_code == 422


def test_put_nonexistent_address(client, sample_address):
    response = client.put("/api/v1/addresses/999", json=sample_address)

    assert response.status_code == 404
