def test_agent_crud_flow(client):
    space_id = client.post("/spaces", json={"name": "Lab"}).json()["id"]

    response = client.post(
        "/agents",
        json={
            "space_id": space_id,
            "name": "Thinker",
            "model": "gpt-4o-mini",
            "description": "Context-aware assistant",
        },
    )
    assert response.status_code == 201
    agent = response.json()
    agent_id = agent["id"]
    assert agent["space_id"] == space_id
    assert agent["model"] == "gpt-4o-mini"

    response = client.get("/agents", params={"space_id": space_id})
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 1
    assert agents[0]["id"] == agent_id

    response = client.put(
        f"/agents/{agent_id}",
        json={"description": "Updated description"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"

    detail = client.get(f"/spaces/{space_id}").json()
    assert len(detail["agents"]) == 1
    assert detail["agents"][0]["id"] == agent_id

    response = client.delete(f"/agents/{agent_id}")
    assert response.status_code == 204

    assert client.get(f"/agents/{agent_id}").status_code == 404


def test_create_agent_requires_space(client):
    response = client.post(
        "/agents",
        json={"space_id": 999, "name": "Ghost", "model": "phantom"},
    )
    assert response.status_code == 404
