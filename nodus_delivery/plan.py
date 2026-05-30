"""DeliveryPlan — structured descriptor for outbound message routing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeliveryPlan:
    """Describes where and how to send an agent response.

    Attributes
    ----------
    channel_id:        Channel adapter to use (e.g. ``"slack"``, ``"discord"``).
    peer_id:           Direct recipient's platform ID.  One of *peer_id* or
                       *thread_id* is typically set.
    thread_id:         Thread or topic ID to post in (for threaded channels).
    reply_to_id:       Platform message ID to quote/reply to.
    chunk_size:        Max characters per chunk.  None = use ``ChannelInfo.max_message_length``.
    preserve_markdown: When False, strip markdown before sending.
    metadata:          Channel-specific extras passed through to the adapter.
    """

    channel_id: str
    peer_id: str | None = None
    thread_id: str | None = None
    reply_to_id: str | None = None
    chunk_size: int | None = None
    preserve_markdown: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
