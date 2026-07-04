"""Unit tests for intelliquery.processing.text_cleaner."""

from intelliquery.processing.text_cleaner import (
    clean_document_text,
    count_tokens,
    normalize_whitespace,
    sanitize_quotes,
    strip_redundant_newlines,
)


class TestNormalizeWhitespace:
    def test_replaces_tabs(self):
        assert normalize_whitespace("hello\tworld") == "hello world"

    def test_collapses_multiple_spaces(self):
        assert normalize_whitespace("hello    world") == "hello world"

    def test_strips_leading_trailing(self):
        assert normalize_whitespace("  hello  ") == "hello"

    def test_preserves_single_newlines(self):
        result = normalize_whitespace("line1\nline2")
        assert "line1\nline2" == result


class TestStripRedundantNewlines:
    def test_double_to_single(self):
        assert strip_redundant_newlines("a\n\nb") == "a\nb"

    def test_triple_to_single(self):
        assert strip_redundant_newlines("a\n\n\nb") == "a\nb"

    def test_preserves_single(self):
        assert strip_redundant_newlines("a\nb") == "a\nb"


class TestSanitizeQuotes:
    def test_escapes_double_quotes(self):
        result = sanitize_quotes('He said "hello"')
        assert '\\"' in result

    def test_normalises_smart_quotes(self):
        result = sanitize_quotes("\u201cHello\u201d")
        assert "\u201c" not in result
        assert "\u201d" not in result


class TestCleanDocumentText:
    def test_combined_pipeline(self):
        raw = '  hello\t\t  world\n\n\nfoo "bar"  '
        result = clean_document_text(raw)
        assert "\t" not in result
        assert "\n\n" not in result
        assert "  " not in result  # multiple spaces collapsed


class TestCountTokens:
    def test_returns_positive_int(self):
        count = count_tokens("Hello, world!")
        assert isinstance(count, int)
        assert count > 0

    def test_longer_text_more_tokens(self):
        short = count_tokens("Hi")
        long = count_tokens("This is a significantly longer piece of text with many words")
        assert long > short
