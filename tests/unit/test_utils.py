"""
Unit tests for utility functions.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from utils import allowed_file, cleanup_old_files, format_file_size, validate_pdf_file


class TestAllowedFile:
    """Test file extension validation."""

    def test_allowed_pdf_file(self):
        """Test that PDF files are allowed."""
        assert allowed_file("document.pdf") is True
        assert allowed_file("DOCUMENT.PDF") is True
        assert allowed_file("test.file.pdf") is True

    def test_disallowed_file_types(self):
        """Test that non-PDF files are rejected."""
        assert allowed_file("document.txt") is False
        assert allowed_file("image.jpg") is False
        assert allowed_file("document.docx") is False
        assert allowed_file("file") is False  # No extension
        assert allowed_file("") is False  # Empty string

    def test_no_extension(self):
        """Test files without extensions."""
        assert allowed_file("filename") is False
        assert allowed_file(".hidden") is False


class TestFormatFileSize:
    """Test file size formatting."""

    def test_bytes(self):
        """Test byte formatting."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(1) == "1.0 B"
        assert format_file_size(512) == "512.0 B"

    def test_kilobytes(self):
        """Test kilobyte formatting."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(2048) == "2.0 KB"

    def test_megabytes(self):
        """Test megabyte formatting."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 1.5) == "1.5 MB"
        assert format_file_size(1024 * 1024 * 10) == "10.0 MB"

    def test_gigabytes(self):
        """Test gigabyte formatting."""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_file_size(1024 * 1024 * 1024 * 2.5) == "2.5 GB"


class TestValidatePdfFile:
    """Test PDF file validation."""

    @patch("utils.fitz")
    def test_valid_pdf(self, mock_fitz):
        """Test validation of a valid PDF."""
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=5)  # 5 pages
        mock_fitz.open.return_value = mock_doc

        result = validate_pdf_file("/fake/path.pdf")
        assert result == (True, "Valid PDF with 5 pages")
        mock_doc.close.assert_called_once()

    @patch("utils.fitz")
    def test_empty_pdf(self, mock_fitz):
        """Test validation of an empty PDF."""
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=0)  # 0 pages
        mock_fitz.open.return_value = mock_doc

        result = validate_pdf_file("/fake/path.pdf")
        assert result == (False, "PDF file is empty")

    @patch("utils.fitz")
    def test_too_many_pages(self, mock_fitz):
        """Test validation of PDF with too many pages."""
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=25)  # 25 pages (>20 limit)
        mock_fitz.open.return_value = mock_doc

        result = validate_pdf_file("/fake/path.pdf")
        assert result == (False, "PDF has 25 pages. Maximum 20 pages allowed.")

    @patch("utils.fitz")
    def test_invalid_pdf(self, mock_fitz):
        """Test validation of an invalid PDF file."""
        mock_fitz.open.side_effect = Exception("Invalid PDF")

        result = validate_pdf_file("/fake/path.pdf")
        assert result[0] is False
        assert "Invalid PDF file: Invalid PDF" in result[1]


class TestCleanupOldFiles:
    """Test file cleanup functionality."""

    def test_cleanup_old_files(self):
        """Test cleanup of old files."""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            old_file = os.path.join(temp_dir, "old_file.txt")
            new_file = os.path.join(temp_dir, "new_file.txt")

            # Create files
            with open(old_file, "w") as f:
                f.write("old content")
            with open(new_file, "w") as f:
                f.write("new content")

            # Mock file modification times
            import time

            old_time = time.time() - (25 * 3600)  # 25 hours ago
            new_time = time.time() - (1 * 3600)  # 1 hour ago

            os.utime(old_file, (old_time, old_time))
            os.utime(new_file, (new_time, new_time))

            # Run cleanup (24 hour threshold)
            cleanup_old_files(temp_dir, max_age_hours=24)

            # Check results
            assert not os.path.exists(old_file)  # Should be deleted
            assert os.path.exists(new_file)  # Should remain

    def test_cleanup_handles_exceptions(self):
        """Test that cleanup handles exceptions gracefully."""
        # This should not raise any exceptions
        cleanup_old_files("/nonexistent/directory", max_age_hours=24)

        # Test with invalid max_age_hours
        cleanup_old_files("/tmp", max_age_hours=-1)
