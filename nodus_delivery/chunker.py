"""Chunking strategies for splitting long content into channel-size pieces."""
from __future__ import annotations

import re

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable  # type: ignore[assignment]


@runtime_checkable
class ChunkStrategy(Protocol):
    """Protocol for all content chunking strategies."""

    def chunk(self, content: str, max_length: int) -> list[str]:
        """Split *content* into chunks no longer than *max_length* characters."""
        ...


class SizeChunker:
    """Split content at word boundaries, never exceeding *max_length* chars per chunk."""

    def chunk(self, content: str, max_length: int) -> list[str]:
        if not content:
            return []
        if len(content) <= max_length:
            return [content]

        chunks: list[str] = []
        while len(content) > max_length:
            # Find the last space before max_length
            split_at = content.rfind(" ", 0, max_length)
            if split_at <= 0:
                split_at = max_length   # hard split if no space found
            chunks.append(content[:split_at].rstrip())
            content = content[split_at:].lstrip()
        if content:
            chunks.append(content)
        return chunks


class ParagraphChunker:
    """Split on paragraph boundaries first; fall back to SizeChunker for long paragraphs.

    Args:
        fallback_size: Max length passed to SizeChunker when a paragraph is too long.
    """

    def __init__(self, fallback_size: int = 4000) -> None:
        self._fallback = SizeChunker()
        self._fallback_size = fallback_size

    def chunk(self, content: str, max_length: int) -> list[str]:
        if not content:
            return []
        if len(content) <= max_length:
            return [content]

        paragraphs = re.split(r"\n{2,}", content)
        chunks: list[str] = []
        current = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            candidate = (current + "\n\n" + para).strip() if current else para
            if len(candidate) <= max_length:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                if len(para) > max_length:
                    # Paragraph itself is too long — fall back to size chunker
                    chunks.extend(self._fallback.chunk(para, self._fallback_size))
                    current = ""
                else:
                    current = para

        if current:
            chunks.append(current)
        return chunks or [content]


class MarkdownBlockChunker:
    """Preserve code blocks, headers, and list items; split between them.

    Never splits inside a fenced code block.  Falls back to SizeChunker when
    an individual block exceeds *max_length*.

    Args:
        fallback_size: Max length for the internal SizeChunker fallback.
    """

    def __init__(self, fallback_size: int = 4000) -> None:
        self._fallback = SizeChunker()
        self._fallback_size = fallback_size

    def chunk(self, content: str, max_length: int) -> list[str]:
        if not content:
            return []
        if len(content) <= max_length:
            return [content]

        # Split into logical blocks (fenced code blocks stay intact)
        blocks = self._split_blocks(content)
        chunks: list[str] = []
        current = ""

        for block in blocks:
            candidate = (current + "\n\n" + block).strip() if current else block
            if len(candidate) <= max_length:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                if len(block) > max_length:
                    chunks.extend(self._fallback.chunk(block, self._fallback_size))
                    current = ""
                else:
                    current = block

        if current:
            chunks.append(current)
        return chunks or [content]

    @staticmethod
    def _split_blocks(content: str) -> list[str]:
        """Split into logical blocks preserving fenced code blocks."""
        blocks: list[str] = []
        in_fence = False
        current: list[str] = []

        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                if in_fence:
                    current.append(line)
                    blocks.append("\n".join(current))
                    current = []
                    in_fence = False
                else:
                    if current:
                        blocks.append("\n".join(current))
                        current = []
                    in_fence = True
                    current = [line]
            elif in_fence:
                current.append(line)
            elif not stripped:
                if current:
                    blocks.append("\n".join(current))
                    current = []
            else:
                current.append(line)

        if current:
            blocks.append("\n".join(current))
        return [b for b in blocks if b.strip()]


# ── Markdown stripping ─────────────────────────────────────────────────────────

_MD_PATTERNS = [
    (re.compile(r"```[\s\S]*?```"), ""),          # fenced code blocks
    (re.compile(r"`[^`]+`"), ""),                  # inline code
    (re.compile(r"^#{1,6}\s*", re.MULTILINE), ""),# headers
    (re.compile(r"\*\*(.+?)\*\*"), r"\1"),         # bold
    (re.compile(r"\*(.+?)\*"), r"\1"),             # italic
    (re.compile(r"__(.+?)__"), r"\1"),             # bold alt
    (re.compile(r"_(.+?)_"), r"\1"),               # italic alt
    (re.compile(r"~~(.+?)~~"), r"\1"),             # strikethrough
    (re.compile(r"\[([^\]]+)\]\([^)]+\)"), r"\1"), # links
    (re.compile(r"^[-*+]\s+", re.MULTILINE), ""),  # list bullets
    (re.compile(r"^\d+\.\s+", re.MULTILINE), ""), # numbered lists
    (re.compile(r"^>\s+", re.MULTILINE), ""),      # blockquotes
]


def strip_markdown(content: str) -> str:
    """Remove common markdown formatting, returning plain text."""
    result = content
    for pattern, replacement in _MD_PATTERNS:
        result = pattern.sub(replacement, result)
    # Collapse multiple blank lines
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()
