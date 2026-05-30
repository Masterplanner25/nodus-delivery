from nodus_delivery import DeliveryPlan


def test_plan_required_fields():
    p = DeliveryPlan(channel_id="slack")
    assert p.channel_id == "slack"
    assert p.peer_id is None
    assert p.thread_id is None
    assert p.reply_to_id is None
    assert p.chunk_size is None
    assert p.preserve_markdown is True
    assert p.metadata == {}


def test_plan_all_fields():
    p = DeliveryPlan(
        channel_id="discord",
        peer_id="U123",
        thread_id="T456",
        reply_to_id="M789",
        chunk_size=2000,
        preserve_markdown=False,
        metadata={"type": "dm"},
    )
    assert p.peer_id == "U123"
    assert p.thread_id == "T456"
    assert p.chunk_size == 2000
    assert p.preserve_markdown is False
    assert p.metadata["type"] == "dm"
