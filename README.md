# nodus-delivery

**Outbound routing, chunking, and delivery planning for multi-channel AI systems.**

Resolves the right channel adapter for a response, splits long content into
channel-appropriate chunks, and delivers each chunk in order. Depends on
[nodus-channels](https://github.com/Masterplanner25/nodus-channels) for the
`ChannelRegistry` and `ChannelAdapter` protocol.

> **Status:** v0.1.0 — published on [PyPI](https://pypi.org/project/nodus-delivery/).

---

## Install

```bash
pip install nodus-delivery
```

Requires `nodus-channels>=0.1.0`.

---

## What it provides

| Component | Purpose |
|---|---|
| `DeliveryPlan` | Describes where and how to send a response |
| `SizeChunker` | Split at word boundaries up to a max character count |
| `ParagraphChunker` | Split on paragraph breaks, respecting a max size |
| `MarkdownBlockChunker` | Preserve code blocks and headers across splits |
| `strip_markdown` | Remove markdown formatting → plain text |
| `DeliveryRouter` | Resolve adapter, chunk, and send; build plan from inbound message |

---

## Quick start

```python
from nodus_channels import ChannelRegistry
from nodus_delivery import DeliveryRouter, DeliveryPlan, SizeChunker

registry = ChannelRegistry()
registry.register(my_slack_adapter)

router = DeliveryRouter(registry, default_chunker=SizeChunker(max_chars=2000))

plan = DeliveryPlan(
    channel_id="slack",
    peer_id="U123",
    content="A very long response that may need chunking...",
)

await router.deliver(plan)
```

---

## DeliveryPlan

```python
from nodus_delivery import DeliveryPlan

plan = DeliveryPlan(
    channel_id="slack",
    peer_id="U123",
    content="Response text",
    thread_id="T456",       # optional: reply in a thread
    reply_to_id="M789",     # optional: reply to a specific message
    strip_md=False,         # strip markdown before chunking (default False)
    chunker=None,           # override router's default chunker
)
```

---

## Chunking strategies

### SizeChunker

Splits at word boundaries. Safe for any channel.

```python
from nodus_delivery import SizeChunker
chunker = SizeChunker(max_chars=2000)
chunks = chunker.chunk("Long text...")   # list[str]
```

### ParagraphChunker

Splits on `\n\n` paragraph breaks first; falls back to size if a paragraph
exceeds `max_chars`.

```python
from nodus_delivery import ParagraphChunker
chunker = ParagraphChunker(max_chars=2000)
```

### MarkdownBlockChunker

Keeps code fences (` ``` `) and headers (`#`, `##`) intact. Never splits
inside a code block.

```python
from nodus_delivery import MarkdownBlockChunker
chunker = MarkdownBlockChunker(max_chars=2000)
```

---

## DeliveryRouter

```python
from nodus_delivery import DeliveryRouter

router = DeliveryRouter(
    registry,
    default_chunker=ParagraphChunker(max_chars=2000),
)

# Build a plan from an inbound Message (replies to sender on same channel)
plan = router.plan_from_message(inbound_message, content="Here is my response.")

# Deliver — sends all chunks in order, returns list of message IDs
msg_ids = await router.deliver(plan)
```

If no adapter is registered for `channel_id`, `deliver` raises `KeyError`.

---

## strip_markdown

```python
from nodus_delivery import strip_markdown

plain = strip_markdown("**bold** and `code` and [link](url)")
# → "bold and code and link"
```

Useful when delivering to channels that don't render markdown (e.g., SMS, voice).

---

## Design

- **One required dependency:** `nodus-channels` for `ChannelRegistry`,
  `ChannelAdapter`, and `Message` types.
- **Protocol-based chunking.** Any callable satisfying `ChunkStrategy`
  (`chunk(text) -> list[str]`) works — no inheritance needed.
- **Async delivery.** `DeliveryRouter.deliver()` is async; each chunk is
  awaited in sequence to preserve ordering.

---

## Development

```bash
pip install -e ".[dev]"
# Also install nodus-channels for tests:
pip install -e "C:/dev/nodus-channels"
pytest tests/ -q
```

---

## License

MIT — see [LICENSE](LICENSE).
