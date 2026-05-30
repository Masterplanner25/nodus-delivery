"""DeliveryRouter — resolve adapter, chunk content, and send."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from .chunker import ChunkStrategy, SizeChunker
from .plan import DeliveryPlan

if TYPE_CHECKING:
    from nodus_channels import ChannelRegistry, Message

logger = logging.getLogger(__name__)

_DEFAULT_CHUNK_SIZE = 4000


class DeliveryRouter:
    """Route agent output through the appropriate channel adapter.

    Usage::

        router = DeliveryRouter(registry)
        message_ids = await router.send("Hello world", plan)
    """

    def __init__(self, registry: "ChannelRegistry") -> None:
        self._registry = registry

    async def send(
        self,
        content: str,
        plan: DeliveryPlan,
        *,
        chunker: Optional[ChunkStrategy] = None,
    ) -> list[str]:
        """Resolve adapter, chunk content, and send each chunk.

        Args:
            content:  Text to send (markdown or plain text).
            plan:     ``DeliveryPlan`` describing where to send.
            chunker:  Override chunking strategy.  Defaults to ``SizeChunker``.

        Returns:
            List of platform message IDs (one per chunk sent).

        Raises:
            KeyError: If ``plan.channel_id`` is not registered.
        """
        adapter = self._registry.get(plan.channel_id)
        if adapter is None:
            raise KeyError(
                f"No adapter registered for channel {plan.channel_id!r}. "
                f"Register one with ChannelRegistry.register() first."
            )

        # Apply markdown stripping if needed
        send_content = content
        if not plan.preserve_markdown:
            from .chunker import strip_markdown  # noqa: PLC0415
            send_content = strip_markdown(content)

        # Determine chunk size
        chunk_size = plan.chunk_size
        if chunk_size is None:
            try:
                chunk_size = adapter.info.max_message_length
            except Exception:
                chunk_size = _DEFAULT_CHUNK_SIZE

        # Chunk content
        strategy = chunker or SizeChunker()
        chunks = strategy.chunk(send_content, chunk_size)
        if not chunks:
            chunks = [send_content] if send_content else []

        # Send each chunk
        message_ids: list[str] = []
        prev_id: str | None = plan.reply_to_id

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            msg_id = await adapter.send(
                chunk,
                plan.peer_id or "",
                thread_id=plan.thread_id,
                reply_to_id=prev_id if i == 0 else None,
            )
            message_ids.append(msg_id)
            # Subsequent chunks don't quote the original
            prev_id = None

        return message_ids

    def plan_from_message(
        self,
        source: "Message",
        *,
        reply: bool = True,
    ) -> DeliveryPlan:
        """Build a ``DeliveryPlan`` for replying to *source*.

        Args:
            source: The inbound message to reply to.
            reply:  When True, set ``reply_to_id`` to quote the source message.

        Returns:
            A ``DeliveryPlan`` targeting the same channel, peer, and thread.
        """
        return DeliveryPlan(
            channel_id=source.channel_id,
            peer_id=source.sender.id,
            thread_id=source.thread_id,
            reply_to_id=source.id if reply else None,
        )
