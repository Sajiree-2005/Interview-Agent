"""Integration tests for the interview flow."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_CANDIDATE = {
    "member": {
        "id": "TEST-001",
        "name": "Test Candidate",
        "jobRole": "Software Engineer",
        "yearsExperience": 3,
        "education": "BS Computer Science",
        "status": "COMPLETED"
    },
    "missions": [
        {"day": 7, "title": "Embeddings Explained", "passed": True, "attempts": 1},
        {"day": 8, "title": "Vector Databases Overview", "passed": True, "attempts": 2},
        {"day": 12, "title": "Prompt Engineering Fundamentals", "passed": True, "attempts": 1},
        {"day": 22, "title": "Multi-Agent Orchestration", "passed": True, "attempts": 3},
    ],
    "signals": {"commitDays": 20, "missionsCompleted": 25, "missionsFirstTry": 15}
}


class TestInterviewFlow:
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_start_interview(self):
        response = client.post("/api/interview", json={
            "sessionId": "test-session-1",
            "candidate": SAMPLE_CANDIDATE
        })
        assert response.status_code == 200
        data = response.json()
        assert data["done"] is False
        assert len(data["reply"]) > 10

    def test_answer_and_continue(self):
        session_id = "test-session-2"
        # Start
        r1 = client.post("/api/interview", json={
            "sessionId": session_id,
            "candidate": SAMPLE_CANDIDATE
        })
        assert r1.status_code == 200

        # Answer
        r2 = client.post("/api/interview", json={
            "sessionId": session_id,
            "message": "Embeddings are vector representations of text that capture semantic meaning."
        })
        assert r2.status_code == 200
        assert r2.json()["done"] is False

    def test_dont_know_response(self):
        session_id = "test-session-3"
        client.post("/api/interview", json={
            "sessionId": session_id,
            "candidate": SAMPLE_CANDIDATE
        })
        r = client.post("/api/interview", json={
            "sessionId": session_id,
            "message": "I don't know"
        })
        assert r.status_code == 200
        assert "fine" in r.json()["reply"].lower() or "okay" in r.json()["reply"].lower()

    def test_session_not_found(self):
        r = client.post("/api/interview", json={
            "sessionId": "nonexistent",
            "message": "hello"
        })
        assert r.status_code == 200
        assert "not found" in r.json()["reply"].lower()
