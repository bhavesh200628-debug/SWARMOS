"""
SWARMOS Telemetry Broadcaster
Maintains WebSocket client channels and broadcasts live digital twin telemetry and AI decision streams.
"""
import asyncio
import json
import logging
from typing import Set
from fastapi import WebSocket

logger = logging.getLogger("swarmos.telemetry")

class TelemetryBroadcaster:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected to telemetry stream. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected from telemetry stream. Total active: {len(self.active_connections)}")

    async def broadcast_state(self, state_dict: dict):
        if not self.active_connections:
            return

        payload = json.dumps({"type": "telemetry_update", "data": state_dict})
        stale_connections = set()

        for conn in self.active_connections:
            try:
                await conn.send_text(payload)
            except Exception:
                stale_connections.add(conn)

        for stale in stale_connections:
            self.disconnect(stale)

    async def broadcast_event(self, event_type: str, event_data: dict):
        if not self.active_connections:
            return

        payload = json.dumps({"type": event_type, "data": event_data})
        stale_connections = set()

        for conn in self.active_connections:
            try:
                await conn.send_text(payload)
            except Exception:
                stale_connections.add(conn)

        for stale in stale_connections:
            self.disconnect(stale)

# Global broadcaster singleton
telemetry_broadcaster = TelemetryBroadcaster()
