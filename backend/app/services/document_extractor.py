from __future__ import annotations

from pathlib import Path


class UnsupportedDocumentTypeError(ValueError):
    pass


class DocumentExtractor:
    def extract_text(self, file_path: str | Path) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf(path)
        if suffix == ".docx":
            return self._extract_docx(path)
        if suffix == ".doc":
            raise UnsupportedDocumentTypeError("Legacy .doc files are not supported in v1")
        raise UnsupportedDocumentTypeError(f"Unsupported file type: {suffix}")

    def _extract_pdf(self, path: Path) -> str:
        try:
            import fitz
        except ImportError as exc:  # pragma: no cover - dependency setup issue
            raise RuntimeError("PyMuPDF is required to process PDF files") from exc

        document = fitz.open(path)
        try:
            text = "\n".join(page.get_text("text") for page in document)
        finally:
            document.close()
        return text.strip()

    def _extract_docx(self, path: Path) -> str:
        try:
            import docx2txt
        except ImportError as exc:  # pragma: no cover - dependency setup issue
            raise RuntimeError("docx2txt is required to process DOCX files") from exc
        return docx2txt.process(str(path)).strip()
