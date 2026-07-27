from pathlib import Path

from utils.ragger import Ragger


class FakeParser:
    def extract(self, pdf_bytes: bytes) -> list[str]:
        return [pdf_bytes.decode()]


def test_same_filename_and_hash_replaces_existing_chunks(tmp_path: Path) -> None:
    ragger = Ragger()
    ragger.text_parser = FakeParser()

    first = ragger.ingest_many([("guide.pdf", b"first")], tmp_path)
    # Simulate a duplicate left by an earlier interrupted indexing attempt.
    ragger.opensearch.index_chunks([dict(ragger.opensearch.chunks[0])])
    second = ragger.ingest_many([("guide.pdf", b"first")], tmp_path)
    expected_hash = ragger.hasher.digest(b"first")

    assert first["total_chunks"] == 1
    assert second["total_chunks"] == 1
    assert first["files"][0]["document_hash"] == expected_hash
    assert second["files"][0]["document_hash"] == expected_hash
    assert len(ragger.opensearch.chunks) == 1
    assert ragger.opensearch.chunks[0]["stored_filename"] == "guide.pdf"
    assert ragger.opensearch.chunks[0]["document_hash"] == expected_hash
    assert (tmp_path / "guide.pdf").read_bytes() == b"first"


def test_different_content_keeps_original_and_uses_sequential_suffixes(tmp_path: Path) -> None:
    ragger = Ragger()
    ragger.text_parser = FakeParser()

    first = ragger.ingest_many([("guide.pdf", b"first")], tmp_path)
    second = ragger.ingest_many([("guide.pdf", b"second")], tmp_path)
    third = ragger.ingest_many([("guide.pdf", b"third")], tmp_path)

    assert [record["stored_filename"] for record in (first["files"][0], second["files"][0], third["files"][0])] == [
        "guide.pdf",
        "guide_1.pdf",
        "guide_2.pdf",
    ]
    assert (tmp_path / "guide.pdf").read_bytes() == b"first"
    assert (tmp_path / "guide_1.pdf").read_bytes() == b"second"
    assert (tmp_path / "guide_2.pdf").read_bytes() == b"third"
