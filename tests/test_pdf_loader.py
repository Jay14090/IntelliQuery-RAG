"""Unit tests for intelliquery.processing.pdf_loader."""

from unittest.mock import MagicMock, patch

from intelliquery.processing.pdf_loader import extract_full_text, split_into_sections


class TestSplitIntoSections:
    def test_dune_style_split(self):
        raw = (
            "Some preamble text.\n"
            "BOOK ONE Something Here\n"
            "Content of book one goes here with many words.\n"
            "BOOK TWO Another Section\n"
            "Content of book two goes here with many words too."
        )
        docs = split_into_sections(raw)
        assert len(docs) >= 2
        assert docs[0].metadata["section"] == 1
        assert "book one" in docs[0].metadata["header"].lower()

    def test_no_match_returns_full_text(self):
        raw = "This text has no chapter markers at all. It is just plain text."
        docs = split_into_sections(raw)
        assert len(docs) == 1
        assert docs[0].metadata["header"] == "Full Text"

    def test_custom_pattern(self):
        raw = "CHAPTER 1 First chapter content here is long enough. CHAPTER 2 Second chapter content here is also long enough."
        docs = split_into_sections(raw, pattern=r"(CHAPTER \d+)")
        assert len(docs) >= 2

    def test_skips_trivially_short_fragments(self):
        raw = "BOOK ONE X BOOK TWO Content of book two with enough meaningful text to pass the threshold."
        docs = split_into_sections(raw)
        # "X" is too short (< 50 chars), should be skipped
        for doc in docs:
            assert len(doc.page_content) > 10


class TestExtractFullText:
    @patch("intelliquery.processing.pdf_loader.PyPDF2.PdfReader")
    def test_concatenates_pages(self, mock_reader_cls):
        page1 = MagicMock()
        page1.extract_text.return_value = "Page one text."
        page2 = MagicMock()
        page2.extract_text.return_value = "Page two text."
        mock_reader = MagicMock()
        mock_reader.pages = [page1, page2]
        mock_reader_cls.return_value = mock_reader

        with patch("builtins.open", MagicMock()):
            result = extract_full_text("fake.pdf")

        assert "Page one text." in result
        assert "Page two text." in result
