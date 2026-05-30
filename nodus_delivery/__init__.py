"""nodus-delivery — outbound routing, chunking, and delivery planning.

Depends on nodus-channels for ChannelRegistry, ChannelAdapter, and Message types.

Plan:
    DeliveryPlan     — describes where and how to send a response

Chunking:
    ChunkStrategy    — protocol all chunkers satisfy
    SizeChunker      — split at word boundaries
    ParagraphChunker — split on paragraph breaks
    MarkdownBlockChunker — preserve code blocks and headers
    strip_markdown   — remove markdown formatting → plain text

Router:
    DeliveryRouter   — resolve adapter, chunk, send; plan_from_message()
"""
from .chunker import (
    ChunkStrategy,
    MarkdownBlockChunker,
    ParagraphChunker,
    SizeChunker,
    strip_markdown,
)
from .plan import DeliveryPlan
from .router import DeliveryRouter

__all__ = [
    "DeliveryPlan",
    "ChunkStrategy",
    "SizeChunker",
    "ParagraphChunker",
    "MarkdownBlockChunker",
    "strip_markdown",
    "DeliveryRouter",
]
