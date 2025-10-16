def test_artifact_crud_flow(client):
    space_id = client.post("/spaces", json={"name": "Ideas"}).json()["id"]

    response = client.post(
        "/artifacts",
        json={"space_id": space_id, "title": "Sketch", "content": "Rough concept"},
    )
    assert response.status_code == 201
    artifact = response.json()
    artifact_id = artifact["id"]
    assert artifact["space_id"] == space_id
    assert artifact["summary"]
    assert isinstance(artifact["tags"], list)
    assert any(tag in {"sketch", "rough", "concept"} for tag in artifact["tags"])

    response = client.get("/artifacts", params={"space_id": space_id})
    assert response.status_code == 200
    listed = response.json()
    assert len(listed) == 1
    assert listed[0]["summary"]

    response = client.put(
        f"/artifacts/{artifact_id}",
        json={"content": "Refined concept"},
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Refined concept"
    assert response.json()["summary"]

    response = client.delete(f"/artifacts/{artifact_id}")
    assert response.status_code == 204

    response = client.get(f"/artifacts/{artifact_id}")
    assert response.status_code == 404


def test_create_artifact_requires_existing_space(client):
    response = client.post(
        "/artifacts",
        json={"space_id": 999, "title": "Ghost", "content": "No space"},
    )
    assert response.status_code == 404


def test_file_upload_artifact(client):
    space_id = client.post("/spaces", json={"name": "Uploads"}).json()["id"]

    response = client.post(
        "/artifacts/upload",
        data={"space_id": str(space_id), "title": "Upload Title"},
        files={"file": ("sample.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 201
    artifact = response.json()
    assert artifact["file_path"] is not None
    assert artifact["file_name"] == "sample.txt"
    assert artifact["summary"]
    assert "upload" in artifact["tags"] or artifact["tags"] == []

    delete_response = client.delete(f"/artifacts/{artifact['id']}")
    assert delete_response.status_code == 204


def test_search_artifacts_api(client):
    space_id = client.post("/spaces", json={"name": "Search"}).json()["id"]
    client.post(
        "/artifacts",
        json={"space_id": space_id, "title": "Deep Work", "content": "Focus"},
    )
    client.post(
        "/artifacts",
        json={"space_id": space_id, "title": "Shallow Work", "content": "Emails"},
    )

    response = client.get("/artifacts/search", params={"q": "deep", "space_id": space_id})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Deep Work"
    assert results[0]["summary"]
