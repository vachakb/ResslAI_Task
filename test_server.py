"""
Test suite for MCP Keyword Search Server

Tests the search_keyword_tool function with various scenarios.
Run with: pytest test_server.py -v
"""
import pytest
import tempfile
import os
from pathlib import Path
from server import search_keyword_tool
from fastapi import HTTPException


class TestSearchKeywordTool:
    """Test cases for the search_keyword_tool function"""

    def test_search_basic_match(self):
        """Test basic keyword search with matches"""
        # Create a temporary file with test content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("First line\n")
            f.write("Second line with keyword\n")
            f.write("Third line\n")
            f.write("Fourth line with KEYWORD too\n")
            temp_path = f.name

        try:
            result = search_keyword_tool({
                "file_path": temp_path,
                "keyword": "keyword"
            })
            
            assert result["count"] == 2
            assert len(result["matches"]) == 2
            assert result["matches"][0]["line"] == 2
            assert "keyword" in result["matches"][0]["text"].lower()
            assert result["matches"][1]["line"] == 4
        finally:
            os.unlink(temp_path)

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Project Alpha\n")
            f.write("project beta\n")
            f.write("PROJECT GAMMA\n")
            f.write("No match here\n")
            temp_path = f.name

        try:
            result = search_keyword_tool({
                "file_path": temp_path,
                "keyword": "project"
            })
            
            assert result["count"] == 3
            assert len(result["matches"]) == 3
        finally:
            os.unlink(temp_path)

    def test_search_no_matches(self):
        """Test search when keyword is not found"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("First line\n")
            f.write("Second line\n")
            temp_path = f.name

        try:
            result = search_keyword_tool({
                "file_path": temp_path,
                "keyword": "notfound"
            })
            
            assert result["count"] == 0
            assert len(result["matches"]) == 0
        finally:
            os.unlink(temp_path)

    def test_search_sample_file(self):
        """Test search with the actual sample.txt file"""
        # This test only runs if sample.txt exists
        sample_path = "sample.txt"
        if not Path(sample_path).exists():
            pytest.skip("sample.txt not found")

        
        result = search_keyword_tool({
            "file_path": sample_path,
            "keyword": "Salesforce"
        })
        
        
        assert result["count"] >= 1
        assert len(result["matches"]) >= 1
        assert all("Salesforce" in m["text"] or "salesforce" in m["text"].lower() for m in result["matches"])

    def test_search_empty_file(self):
        """Test search on an empty file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            temp_path = f.name
           

        try:
            result = search_keyword_tool({
                "file_path": temp_path,
                "keyword": "anything"
            })
            
            assert result["count"] == 0
            assert len(result["matches"]) == 0
        finally:
            os.unlink(temp_path)

    def test_search_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent file"""
        with pytest.raises(HTTPException) as exc_info:
            search_keyword_tool({
                "file_path": "nonexistent_file.txt",
                "keyword": "test"
            })
        
        assert exc_info.value.status_code == 400
        assert "File not found" in str(exc_info.value.detail)

    def test_search_missing_arguments(self):
        """Test that missing arguments raise appropriate errors"""
        # Missing file_path
        with pytest.raises(HTTPException) as exc_info:
            search_keyword_tool({"keyword": "test"})
        assert exc_info.value.status_code == 400
        
        # Missing keyword
        with pytest.raises(HTTPException) as exc_info:
            search_keyword_tool({"file_path": "test.txt"})
        assert exc_info.value.status_code == 400

    def test_search_line_numbers_correct(self):
        """Test that line numbers are correctly reported (1-based)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Line 1\n")
            f.write("Line 2 match\n")
            f.write("Line 3\n")
            f.write("Line 4 match\n")
            f.write("Line 5 match\n")
            temp_path = f.name

        try:
            result = search_keyword_tool({
                "file_path": temp_path,
                "keyword": "match"
            })
            
            assert result["matches"][0]["line"] == 2
            assert result["matches"][1]["line"] == 4
            assert result["matches"][2]["line"] == 5
        finally:
            os.unlink(temp_path)

    def test_search_preserves_line_text(self):
        """Test that original line text is preserved (without trailing newline)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            test_line = "This is a test line with keyword"
            f.write(f"{test_line}\n")
            temp_path = f.name

        try:
            result = search_keyword_tool({
                "file_path": temp_path,
                "keyword": "keyword"
            })
            
            assert result["matches"][0]["text"] == test_line
            assert "\n" not in result["matches"][0]["text"]
        finally:
            os.unlink(temp_path)


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_search_special_characters(self):
        """Test search with special characters"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Line with special chars: @#$%\n")
            f.write("Line with @#$ in it\n")
            temp_path = f.name

        try:
            result = search_keyword_tool({
                "file_path": temp_path,
                "keyword": "@#$"
            })
            
            assert result["count"] == 2
        finally:
            os.unlink(temp_path)

    def test_search_unicode(self):
        """Test search with unicode characters"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Hello 世界\n")
            f.write("世界 is world\n")
            temp_path = f.name

        try:
            result = search_keyword_tool({
                "file_path": temp_path,
                "keyword": "世界"
            })
            
            assert result["count"] == 2
        finally:
            os.unlink(temp_path)

    def test_search_long_lines(self):
        """Test search with very long lines"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            long_line = "a" * 10000 + " keyword " + "b" * 10000
            f.write(f"{long_line}\n")
            temp_path = f.name

        try:
            result = search_keyword_tool({
                "file_path": temp_path,
                "keyword": "keyword"
            })
            
            assert result["count"] == 1
            assert "keyword" in result["matches"][0]["text"]
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
   
    pytest.main([__file__, "-v"])
