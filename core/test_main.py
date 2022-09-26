from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_read_main():
    response = client.get("/posts/?skip=0&limit=10")
    assert response.status_code == 200
