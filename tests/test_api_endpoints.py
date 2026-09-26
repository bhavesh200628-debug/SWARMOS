"""
Integration Tests for SWARMOS FastAPI HTTP Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_health_endpoints():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["service"] == "SWARMOS"

    r_ai = client.get("/health/ai")
    assert r_ai.status_code == 200
    assert r_ai.json()["status"] == "operational"

    r_sim = client.get("/health/simulation")
    assert r_sim.status_code == 200
    assert r_sim.json()["status"] in ["running", "paused"]

def test_fleet_endpoints():
    r = client.get("/api/fleet")
    assert r.status_code == 200
    robots = r.json()
    assert len(robots) >= 3
    assert any(b["id"] == "robot_a" for b in robots)

    r_bot = client.get("/api/robots/robot_a")
    assert r_bot.status_code == 200
    assert r_bot.json()["name"] == "Alpha (Scout-01)"

def test_mission_submission():
    payload = {"prompt": "Inspect Zone B and verify quarantine"}
    r = client.post("/api/missions", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["natural_language_prompt"] == payload["prompt"]
    assert len(data["tasks"]) >= 3

def test_demo_lifecycle():
    r_reset = client.post("/api/demo/reset")
    assert r_reset.status_code == 200
    assert r_reset.json()["status"] == "reset_complete"

    r_run = client.post("/api/demo/run")
    assert r_run.status_code == 200
    assert r_run.json()["status"] == "demo_started"

    r_status = client.get("/api/demo/status")
    assert r_status.status_code == 200

def test_evaluate_endpoint():
    r = client.post("/api/evaluate")
    assert r.status_code == 200
    data = r.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) == 5
    assert data["summary"]["mission_completion_rate"] == 100.0
