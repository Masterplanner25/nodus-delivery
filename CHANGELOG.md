# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] — 2026-05-30

Initial release — prepared, not yet published.

### Added

- **`DeliveryPlan`** — response delivery descriptor. Fields: `channel_id`,
  `peer_id`, `content`, optional `thread_id`, `reply_to_id`, `strip_md`
  (default False), `chunker` (overrides router default).

- **`ChunkStrategy`** — protocol: `chunk(text: str) -> list[str]`.

- **`SizeChunker`** — splits at word boundaries up to `max_chars` per chunk.

- **`ParagraphChunker`** — splits on `\n\n` paragraph breaks; falls back to
  size splitting when a paragraph exceeds `max_chars`.

- **`MarkdownBlockChunker`** — preserves code fences and headers intact;
  never splits inside a ` ``` ` block.

- **`strip_markdown(text)`** — removes markdown formatting to produce plain
  text suitable for non-rendering channels.

- **`DeliveryRouter`** — resolves a `ChannelAdapter` from `ChannelRegistry`,
  chunks the content, and sends each chunk in order.
  `deliver(plan) -> list[str]` (async, returns message IDs).
  `plan_from_message(message, content)` builds a `DeliveryPlan` that replies
  to the inbound message's peer on the same channel.

- **27 tests** across three test files (chunker, plan, router).

- **One required dependency:** `nodus-channels>=0.1.0`.

[0.1.0]: https://github.com/Masterplanner25/nodus-delivery/releases/tag/v0.1.0
