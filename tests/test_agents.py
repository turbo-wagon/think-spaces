def test_agent_crud_flow(client):
    space_id = client.post("/spaces", json={"name": "Lab"}).json()["id"]

    response = client.post(
        "/agents",
        json={
            "space_id": space_id,
            "name": "Thinker",
            "model": "gpt-4o-mini",
            "provider": "echo",
            "description": "Context-aware assistant",
        },
    )
    assert response.status_code == 201
    agent = response.json()
    agent_id = agent["id"]
    assert agent["space_id"] == space_id
    assert agent["model"] == "gpt-4o-mini"
    assert agent["provider"] == "echo"

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
    assert response.json()["provider"] == "echo"

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


def test_agent_interaction_echo_provider(client):
    space_id = client.post("/spaces", json={"name": "Interact"}).json()["id"]
    # Add artifact for context
    client.post(
        "/artifacts",
        json={"space_id": space_id, "title": "Context note", "content": "Insight"},
    )
    agent = client.post(
        "/agents",
        json={
            "space_id": space_id,
            "name": "Echo",
            "model": "echo",
            "provider": "echo",
        },
    ).json()

    response = client.post(
        f"/agents/{agent['id']}/interact",
        json={"prompt": "Hello world", "context_limit": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Hello world" in data["output"]
    assert data["provider"] == "echo"
    assert isinstance(data["context"], list)
    if data["context"]:
        assert all("type" in item for item in data["context"])


def test_openai_provider_without_key_returns_error(client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    space_id = client.post("/spaces", json={"name": "API"}).json()["id"]
    agent = client.post(
        "/agents",
        json={
            "space_id": space_id,
            "name": "OpenAI",
            "model": "gpt-4o-mini",
            "provider": "openai",
        },
    ).json()

    response = client.post(
        f"/agents/{agent['id']}/interact",
        json={"prompt": "Hello"},
    )
    assert response.status_code == 400
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_ollama_provider_connection_error(client, monkeypatch):
    space_id = client.post("/spaces", json={"name": "Ollama"}).json()["id"]
    agent = client.post(
        "/agents",
        json={
            "space_id": space_id,
            "name": "Local",
            "model": "llama3",
            "provider": "ollama",
        },
    ).json()

    async def fake_generate(self, request):
        raise RuntimeError("Failed to reach Ollama at http://localhost:11434")

    monkeypatch.setattr(
        "app.llm.ollama_provider.OllamaProvider.generate", fake_generate
    )

    response = client.post(
        f"/agents/{agent['id']}/interact",
        json={"prompt": "Ping"},
    )
    assert response.status_code == 400
    assert "Ollama" in response.json()["detail"]


def test_list_agent_interactions(client):
    space_id = client.post("/spaces", json={"name": "History"}).json()["id"]
    agent = client.post(
        "/agents",
        json={
            "space_id": space_id,
            "name": "Echo history",
            "model": "echo",
            "provider": "echo",
        },
    ).json()

    for prompt in ["first", "second"]:
        resp = client.post(
            f"/agents/{agent['id']}/interact",
            json={"prompt": prompt, "context_limit": 0},
        )
        assert resp.status_code == 200

    history = client.get(f"/agents/{agent['id']}/interactions")
    assert history.status_code == 200
    items = history.json()
    assert len(items) == 2
    assert items[0]["prompt"] in {"first", "second"}
    assert isinstance(items[0]["context"], list)
