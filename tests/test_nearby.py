
def test_nearby_search_returns_matching_address(
    client,
    sample_address,
):
    client.post("/api/v1/addresses", json=sample_address)

    response = client.get(
        "/api/v1/addresses/nearby",
        params={
            "latitude": 18.5204,
            "longitude": 73.8567,
            "distance_km": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Home"
    assert data["items"][0]["distance_km"] == 0.0


def test_nearby_search_excludes_far_addresses(
    client,
    sample_address,
):
    client.post("/api/v1/addresses", json=sample_address)

    response = client.get(
        "/api/v1/addresses/nearby",
        params={
            "latitude": 19.0760,
            "longitude": 72.8777,
            "distance_km": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["items"] == []


def test_nearby_search_sorts_by_distance(client, sample_address):
    # Create an address close to the search location.
    close_address = sample_address.copy()
    close_address["name"] = "Close Address"

    # Create an address farther away.
    far_address = sample_address.copy()
    far_address["name"] = "Far Address"
    far_address["latitude"] = 19.0760
    far_address["longitude"] = 72.8777

    client.post("/api/v1/addresses", json=far_address)
    client.post("/api/v1/addresses", json=close_address)

    response = client.get(
        "/api/v1/addresses/nearby",
        params={
            "latitude": 18.5204,
            "longitude": 73.8567,
            "distance_km": 150,
        },
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert len(items) == 2
    assert items[0]["name"] == "Close Address"
    assert items[1]["name"] == "Far Address"

    assert (
        items[0]["distance_km"]
        < items[1]["distance_km"]
    )


def test_nearby_search_respects_limit(client, sample_address):
    for index in range(3):
        address = sample_address.copy()
        address["name"] = f"Address {index + 1}"

        client.post("/api/v1/addresses", json=address)

    response = client.get(
        "/api/v1/addresses/nearby",
        params={
            "latitude": 18.5204,
            "longitude": 73.8567,
            "distance_km": 10,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert len(data["items"]) == 2


def test_nearby_search_rejects_invalid_coordinates(client):
    response = client.get(
        "/api/v1/addresses/nearby",
        params={
            "latitude": 95,
            "longitude": 73.8567,
            "distance_km": 10,
        },
    )

    assert response.status_code == 422


def test_nearby_search_rejects_non_finite_latitude(client):
    response = client.get(
        "/api/v1/addresses/nearby",
        params={
            "latitude": "NaN",
            "longitude": 73.8567,
            "distance_km": 10,
        },
    )

    assert response.status_code == 422


def test_nearby_search_rejects_invalid_distance(client):
    response = client.get(
        "/api/v1/addresses/nearby",
        params={
            "latitude": 18.5204,
            "longitude": 73.8567,
            "distance_km": 0,
        },
    )

    assert response.status_code == 422


def test_nearby_search_works_across_antimeridian(client, sample_address):
    sample_address["latitude"] = 0
    sample_address["longitude"] = 179.9
    client.post("/api/v1/addresses", json=sample_address)

    response = client.get(
        "/api/v1/addresses/nearby",
        params={"latitude": 0, "longitude": -179.9, "distance_km": 30},
    )

    assert response.json()["total"] == 1


def test_nearby_search_excludes_address_outside_latitude_band(
    client,
    sample_address,
):
    # About 111 km north of the search point.
    sample_address["latitude"] = 19.5204
    client.post("/api/v1/addresses", json=sample_address)

    response = client.get(
        "/api/v1/addresses/nearby",
        params={"latitude": 18.5204, "longitude": 73.8567, "distance_km": 50},
    )

    assert response.json()["total"] == 0
