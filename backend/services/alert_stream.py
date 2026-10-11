"""Alert stream publish-subscribe broker for real-time Server-Sent Events (SSE).

Features:
- Tenant-scoped event subscription queues.
- Durable alert broadcast to active subscribers.
- Backpressure prevention and graceful client disconnect cleanup.
- Reconnection support with Last-Event-ID replay caching.
"""
import asyncio
import json
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict, Optional, Set

logger = logging.getLogger(__name__)


class AlertStreamBroker:
    """In-memory tenant-scoped broker for Server-Sent Events streaming."""

    # tenant_id -> set of asyncio.Queue
    _subscribers: Dict[str, Set[asyncio.Queue]] = {}
    # tenant_id -> deque of recent events for reconnection replay (max 100)
    _recent_events: Dict[str, Deque[Dict[str, Any]]] = {}
    _lock = asyncio.Lock()

    @classmethod
    async def subscribe(cls, tenant_id: str) -> asyncio.Queue:
        """Register a new SSE client subscriber queue for a specific tenant."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        async with cls._lock:
            if tenant_id not in cls._subscribers:
                cls._subscribers[tenant_id] = set()
            cls._subscribers[tenant_id].add(queue)
            logger.info("New SSE client subscribed to tenant %s (total: %d)", tenant_id, len(cls._subscribers[tenant_id]))
        return queue

    @classmethod
    async def unsubscribe(cls, tenant_id: str, queue: asyncio.Queue) -> None:
        """Clean up disconnected client queue to prevent memory leaks and backpressure."""
        async with cls._lock:
            if tenant_id in cls._subscribers:
                cls._subscribers[tenant_id].discard(queue)
                if not cls._subscribers[tenant_id]:
                    del cls._subscribers[tenant_id]
            logger.info("SSE client unsubscribed from tenant %s", tenant_id)

    @classmethod
    async def publish_alert(cls, tenant_id: str, alert_data: Dict[str, Any]) -> int:
        """
        Broadcasts an ingested alert to all active subscribers for that tenant.
        Caches the alert in recent events for replay on client reconnection.
        """
        event_id = alert_data.get("alert_id") or f"evt-{datetime.now(timezone.utc).timestamp()}"
        wrapped_event = {
            "id": event_id,
            "event": "alert",
            "data": alert_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Cache in recent events
        async with cls._lock:
            if tenant_id not in cls._recent_events:
                cls._recent_events[tenant_id] = deque(maxlen=100)
            cls._recent_events[tenant_id].append(wrapped_event)

            subscribers = list(cls._subscribers.get(tenant_id, set()))

        delivered = 0
        for queue in subscribers:
            try:
                queue.put_nowait(wrapped_event)
                delivered += 1
            except asyncio.QueueFull:
                logger.warning("Subscriber queue full for tenant %s; dropping event for slow client", tenant_id)

        return delivered

    @classmethod
    async def get_missed_events(cls, tenant_id: str, last_event_id: str) -> list:
        """Returns events that occurred after last_event_id for reconnection replay."""
        async with cls._lock:
            recent = cls._recent_events.get(tenant_id, deque())
            found = False
            missed = []
            for ev in recent:
                if found:
                    missed.append(ev)
                elif ev.get("id") == last_event_id:
                    found = True
            return missed if found else []
