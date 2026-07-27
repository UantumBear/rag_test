from pathlib import Path

from utils.ragger import Ragger


class FakeParser:
    def extract(self, pdf_bytes: bytes) -> list[str]:
        return [pdf_bytes.decode()]


def test_disabled_keyword_extractor_does_not_add_keywords_or_import_dependencies(tmp_path: Path) -> None:
    ragger = Ragger()
    ragger.text_parser = FakeParser()

    result = ragger.ingest_many([("guide.pdf", b"plain document")], tmp_path)

    assert result["files"][0]["warnings"] == []
    assert "keywords" not in ragger.opensearch.chunks[0]


def test_keyword_error_becomes_file_warning_and_other_files_continue(tmp_path: Path) -> None:
    ragger = Ragger()
    ragger.text_parser = FakeParser()
    ragger.keyword_extractor.active = True
    ragger.keyword_extractor.algorithm = "unsupported"

    result = ragger.ingest_many(
        [("first.pdf", b"first text"), ("second.pdf", b"second text")], tmp_path
    )

    assert result["total_chunks"] == 2
    assert all(record["status"] == "completed" for record in result["files"])
    assert all(record["warnings"] for record in result["files"])
    assert all("keywords" not in chunk for chunk in ragger.opensearch.chunks)
