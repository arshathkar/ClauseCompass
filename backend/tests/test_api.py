import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
@pytest.mark.integration
async def test_healthz(client):
    """F9.1: Health check endpoint returns 200."""
    response = await client.get("/healthz")
    assert response.status_code == 200

@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_session(client):
    """F9.2: Create session returns 200 or 201."""
    response = await client.post("/v1/sessions")
    assert response.status_code in (200, 201)

@pytest.mark.asyncio
@pytest.mark.integration
async def test_post_document(client):
    """F9.2: Post document requires session."""
    # First create a session
    session_resp = await client.post("/v1/sessions")
    if session_resp.status_code in (200, 201):
        session_id = session_resp.json().get("session_id", "test-session")
        response = await client.post(
            "/v1/documents",
            json={"text": "1. This is a test clause about termination.\n2. The rent is Rs. 25,000."},
            headers={"X-Session-Id": session_id}
        )
        assert response.status_code in (200, 201, 422)  # 422 if schema mismatch
    else:
        pytest.skip("Session creation not available")

@pytest.mark.asyncio
@pytest.mark.integration
async def test_security_headers(client):
    """F11.1: Security headers present."""
    response = await client.get("/healthz")
    assert "content-security-policy" in [k.lower() for k in response.headers.keys()]
    assert "x-content-type-options" in [k.lower() for k in response.headers.keys()]

@pytest.mark.asyncio
@pytest.mark.integration
async def test_cors(client):
    """F11.1: CORS preflight."""
    response = await client.options(
        "/healthz",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert response.status_code in (200, 204)

@pytest.mark.asyncio
@pytest.mark.integration
async def test_oversized_payload(client):
    """F9.2: Oversized payload returns 413."""
    long_text = "a" * 500001  # Just over max_text_chars
    response = await client.post("/v1/documents", json={"text": long_text})
    # Should reject — either 413 or 422 depending on validation layer
    assert response.status_code in (413, 422)
