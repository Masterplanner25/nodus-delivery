"""DeliveryRouter tests using a stub ChannelAdapter."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from nodus_delivery import DeliveryPlan, DeliveryRouter, SizeChunker


def _make_registry(channel_id="slack", max_length=4000):
    adapter = MagicMock()
    adapter.channel_id = channel_id
    adapter.info.max_message_length = max_length
    adapter.send = AsyncMock(return_value="msg-id-1")

    registry = MagicMock()
    registry.get.return_value = adapter
    return registry, adapter


def _make_source_message(channel_id="slack"):
    from nodus_channels import Message, Peer
    peer = Peer(id="U123", channel_id=channel_id)
    return Message(
        id="orig-msg",
        channel_id=channel_id,
        sender=peer,
        content="hello",
        timestamp=datetime.now(timezone.utc),
        thread_id="T1",
    )


# ── send ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_returns_message_ids():
    registry, adapter = _make_registry()
    router = DeliveryRouter(registry)
    plan = DeliveryPlan(channel_id="slack", peer_id="U123")
    ids = await router.send("Hello world", plan)
    assert len(ids) == 1
    assert ids[0] == "msg-id-1"
    adapter.send.assert_called_once()


@pytest.mark.asyncio
async def test_send_uses_chunk_size_from_plan():
    registry, adapter = _make_registry()
    router = DeliveryRouter(registry)
    plan = DeliveryPlan(channel_id="slack", peer_id="U1", chunk_size=5)
    content = "word " * 10   # > 5 chars
    await router.send(content, plan, chunker=SizeChunker())
    # Should have been called multiple times due to small chunk size
    assert adapter.send.call_count > 1


@pytest.mark.asyncio
async def test_send_strips_markdown_when_preserve_false():
    registry, adapter = _make_registry()
    router = DeliveryRouter(registry)
    plan = DeliveryPlan(channel_id="slack", peer_id="U1", preserve_markdown=False)
    await router.send("**bold** text", plan)
    # The sent content should have bold stripped
    call_args = adapter.send.call_args
    sent_content = call_args[0][0]
    assert "**" not in sent_content
    assert "bold" in sent_content


@pytest.mark.asyncio
async def test_send_raises_keyerror_for_unknown_channel():
    registry = MagicMock()
    registry.get.return_value = None
    router = DeliveryRouter(registry)
    plan = DeliveryPlan(channel_id="unknown")
    with pytest.raises(KeyError, match="unknown"):
        await router.send("hello", plan)


@pytest.mark.asyncio
async def test_send_empty_content_returns_empty():
    registry, adapter = _make_registry()
    router = DeliveryRouter(registry)
    plan = DeliveryPlan(channel_id="slack", peer_id="U1")
    ids = await router.send("", plan)
    assert ids == []
    adapter.send.assert_not_called()


# ── plan_from_message ─────────────────────────────────────────────────────────

def test_plan_from_message_sets_channel_and_peer():
    registry, _ = _make_registry()
    router = DeliveryRouter(registry)
    source = _make_source_message()
    plan = router.plan_from_message(source)
    assert plan.channel_id == "slack"
    assert plan.peer_id == "U123"
    assert plan.thread_id == "T1"


def test_plan_from_message_sets_reply_to_id():
    registry, _ = _make_registry()
    router = DeliveryRouter(registry)
    source = _make_source_message()
    plan = router.plan_from_message(source, reply=True)
    assert plan.reply_to_id == "orig-msg"


def test_plan_from_message_no_reply():
    registry, _ = _make_registry()
    router = DeliveryRouter(registry)
    source = _make_source_message()
    plan = router.plan_from_message(source, reply=False)
    assert plan.reply_to_id is None
