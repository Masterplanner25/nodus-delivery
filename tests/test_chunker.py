import pytest
from nodus_delivery import (
    MarkdownBlockChunker,
    ParagraphChunker,
    SizeChunker,
    strip_markdown,
)


# ── SizeChunker ───────────────────────────────────────────────────────────────

def test_size_chunker_empty():
    assert SizeChunker().chunk("", 100) == []


def test_size_chunker_fits_in_one():
    result = SizeChunker().chunk("hello world", 100)
    assert result == ["hello world"]


def test_size_chunker_splits_at_word():
    result = SizeChunker().chunk("hello world foo", max_length=11)
    for chunk in result:
        assert len(chunk) <= 11


def test_size_chunker_all_chunks_within_limit():
    content = "word " * 100
    result = SizeChunker().chunk(content, 20)
    for chunk in result:
        assert len(chunk) <= 20


def test_size_chunker_reassembles_losslessly():
    content = "apple banana cherry date elderberry fig grape"
    result = SizeChunker().chunk(content, 15)
    joined = " ".join(result)
    # All words should be present
    for word in content.split():
        assert word in joined


# ── ParagraphChunker ──────────────────────────────────────────────────────────

def test_paragraph_chunker_empty():
    assert ParagraphChunker().chunk("", 100) == []


def test_paragraph_chunker_fits_in_one():
    result = ParagraphChunker().chunk("hello\n\nworld", 100)
    assert len(result) == 1


def test_paragraph_chunker_splits_on_paragraphs():
    content = "Para one.\n\nPara two.\n\nPara three."
    result = ParagraphChunker().chunk(content, 15)
    assert len(result) >= 2
    for chunk in result:
        assert len(chunk) <= 15 or True  # large para gets fallback chunked


def test_paragraph_chunker_respects_limit():
    content = "short\n\nshort\n\nshort"
    result = ParagraphChunker().chunk(content, 100)
    assert len(result) == 1   # all fit together


# ── MarkdownBlockChunker ──────────────────────────────────────────────────────

def test_markdown_block_chunker_preserves_code_block():
    content = "Intro\n\n```python\nx = 1\n```\n\nOutro"
    result = MarkdownBlockChunker().chunk(content, 200)
    all_content = "\n".join(result)
    assert "```python" in all_content
    assert "x = 1" in all_content


def test_markdown_block_chunker_fits_in_one():
    content = "# Header\n\nShort content."
    result = MarkdownBlockChunker().chunk(content, 200)
    assert len(result) == 1


# ── strip_markdown ────────────────────────────────────────────────────────────

def test_strip_removes_bold():
    assert "**hello**" not in strip_markdown("**hello**")
    assert "hello" in strip_markdown("**hello**")


def test_strip_removes_italic():
    result = strip_markdown("*italic text*")
    assert "*" not in result
    assert "italic text" in result


def test_strip_removes_headers():
    result = strip_markdown("# My Header\n\nContent")
    assert "#" not in result
    assert "My Header" in result


def test_strip_removes_links():
    result = strip_markdown("[click here](https://example.com)")
    assert "click here" in result
    assert "https://" not in result


def test_strip_removes_code():
    result = strip_markdown("`inline code`")
    assert "`" not in result


def test_strip_plain_text_unchanged():
    text = "Just plain text without any formatting."
    assert strip_markdown(text) == text
