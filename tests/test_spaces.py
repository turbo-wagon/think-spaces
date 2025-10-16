def test_create_and_get_space(client):
    response = client.post(
        "/spaces",
        json={"name": "Notebook", "description": "Research notes"},
    )
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Notebook"
    space_id = created["id"]

    response = client.get("/spaces")
    assert response.status_code == 200
    spaces = response.json()
    assert len(spaces) == 1
    assert spaces[0]["id"] == space_id

    response = client.get(f"/spaces/{space_id}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["artifacts"] == []
    assert detail["agents"] == []


def test_update_and_delete_space(client):
    response = client.post("/spaces", json={"name": "Drafts"})
    space_id = response.json()["id"]

    response = client.put(
        f"/spaces/{space_id}",
        json={"description": "Polished thoughts"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Polished thoughts"

    response = client.delete(f"/spaces/{space_id}")
    assert response.status_code == 204

    response = client.get(f"/spaces/{space_id}")
    assert response.status_code == 404
