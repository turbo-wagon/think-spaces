def test_ui_flows(client):
    # No spaces yet, should show empty state text.
    response = client.get("/ui/spaces")
    assert response.status_code == 200
    assert "No spaces yet" in response.text

    # Create a space through the HTML form.
    response = client.post(
        "/ui/spaces",
        data={"name": "Workshop", "description": "Ideas and notes"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    location = response.headers["Location"]

    # Follow redirect and check content.
    response = client.get(location)
    assert response.status_code == 200
    assert "Workshop" in response.text
    assert "No artifacts yet" in response.text
    assert "No agents yet" in response.text

    # Add artifact
    response = client.post(
        f"{location}/artifacts",
        data={"title": "First note", "content": "Something to remember"},
        files={"file": ("", b"")},
        follow_redirects=False,
    )
    assert response.status_code == 303

    # Add agent
    response = client.post(
        f"{location}/agents",
        data={"name": "Researcher", "model": "gpt-4o-mini", "provider": "echo"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    detail = client.get(location)
    assert "First note" in detail.text
    assert "Researcher" in detail.text
    assert "Tags:" in detail.text

    response = client.post(
        f"{location}/agents/1/chat",
        data={
            "prompt": "Hello agent",
            "system": "Be brief",
            "context_limit": 1,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    detail = client.get(location)
    assert "Hello agent" in detail.text
    assert "Be brief" in detail.text
    assert "Artifact context" in detail.text

    response = client.post(
        f"{location}/agents/1/summarize",
        follow_redirects=False,
    )
    assert response.status_code == 303

    detail = client.get(location)
    assert "Space Memory" in detail.text

    # Update artifact
    response = client.post(
        f"{location}/artifacts/1/update",
        data={"title": "Updated note", "content": "Refined content"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    detail = client.get(location)
    assert "Updated note" in detail.text
    assert "Refined content" in detail.text

    search_page = client.get(f"{location}?q=Updated")
    assert search_page.status_code == 200
    assert "Search results" in search_page.text
    assert "Updated note" in search_page.text

    # Delete artifact
    response = client.post(
        f"{location}/artifacts/1/delete",
        follow_redirects=False,
    )
    assert response.status_code == 303

    detail = client.get(location)
    assert "Updated note" not in detail.text

    # Upload file artifact
    response = client.post(
        f"{location}/artifacts",
        data={"title": "File note", "content": "File attached"},
        files={"file": ("example.txt", b"hello", "text/plain")},
        follow_redirects=False,
    )
    assert response.status_code == 303

    detail = client.get(location)
    assert "File note" in detail.text
    assert "example.txt" in detail.text

    artifacts = client.get("/artifacts", params={"space_id": 1}).json()
    file_artifact_id = next(item["id"] for item in artifacts if item["title"] == "File note")

    response = client.post(
        f"{location}/artifacts/{file_artifact_id}/delete",
        follow_redirects=False,
    )
    assert response.status_code == 303

    detail = client.get(location)
    assert "File note" not in detail.text

    # Update agent
    response = client.post(
        f"{location}/agents/1/update",
        data={
            "name": "Updated Agent",
            "model": "gpt-4o-mini",
            "provider": "echo",
            "description": "Helper",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    detail = client.get(location)
    assert "Updated Agent" in detail.text
    assert "Helper" in detail.text

    # Delete agent
    response = client.post(
        f"{location}/agents/1/delete",
        follow_redirects=False,
    )
    assert response.status_code == 303

    detail = client.get(location)
    assert "Updated Agent" not in detail.text
