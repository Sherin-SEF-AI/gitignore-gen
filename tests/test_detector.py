"""Tests for the technology detector."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from gitignore_gen.detector import TechnologyDetector


@pytest.fixture
def detector():
    """Create a TechnologyDetector instance."""
    return TechnologyDetector()


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


class TestTechnologyDetector:
    """Test cases for TechnologyDetector."""

    @pytest.mark.asyncio
    async def test_detect_python_project(self, detector, temp_dir):
        """Test detection of Python project."""
        # Create Python project structure
        (temp_dir / "requirements.txt").write_text("requests==2.31.0")
        (temp_dir / "main.py").write_text("print('Hello, World!')")
        
        technologies = await detector.detect(temp_dir)
        
        assert "python" in technologies

    @pytest.mark.asyncio
    async def test_detect_node_project(self, detector, temp_dir):
        """Test detection of Node.js project."""
        # Create Node.js project structure
        (temp_dir / "package.json").write_text('{"name": "test-project"}')
        (temp_dir / "index.js").write_text("console.log('Hello, World!');")
        
        technologies = await detector.detect(temp_dir)
        
        assert "node" in technologies

    @pytest.mark.asyncio
    async def test_detect_java_project(self, detector, temp_dir):
        """Test detection of Java project."""
        # Create Java project structure
        (temp_dir / "pom.xml").write_text("<project></project>")
        (temp_dir / "src" / "main" / "java" / "Main.java").write_text("public class Main {}")
        
        technologies = await detector.detect(temp_dir)
        
        assert "java" in technologies

    @pytest.mark.asyncio
    async def test_detect_multiple_technologies(self, detector, temp_dir):
        """Test detection of multiple technologies."""
        # Create project with multiple technologies
        (temp_dir / "requirements.txt").write_text("requests==2.31.0")
        (temp_dir / "package.json").write_text('{"name": "test-project"}')
        (temp_dir / ".vscode" / "settings.json").write_text("{}")
        
        technologies = await detector.detect(temp_dir)
        
        assert "python" in technologies
        assert "node" in technologies
        assert "vscode" in technologies

    @pytest.mark.asyncio
    async def test_detect_no_technologies(self, detector, temp_dir):
        """Test detection when no technologies are present."""
        # Create empty directory
        (temp_dir / "README.md").write_text("# Test Project")
        
        technologies = await detector.detect(temp_dir)
        
        assert len(technologies) == 0

    def test_get_template_name(self, detector):
        """Test template name mapping."""
        assert detector.get_template_name("python") == "python"
        assert detector.get_template_name("node") == "node"
        assert detector.get_template_name("vscode") == "visualstudiocode"
        assert detector.get_template_name("unknown") == "unknown"

    @pytest.mark.asyncio
    async def test_scan_directory_permission_error(self, detector, temp_dir):
        """Test handling of permission errors during scanning."""
        with patch('pathlib.Path.rglob') as mock_rglob:
            mock_rglob.side_effect = PermissionError("Permission denied")
            
            technologies = await detector.detect(temp_dir)
            
            assert len(technologies) == 0

    @pytest.mark.asyncio
    async def test_check_patterns_with_wildcards(self, detector, temp_dir):
        """Test pattern checking with wildcard patterns."""
        # Create files with specific extensions
        (temp_dir / "test.csproj").write_text("<Project></Project>")
        
        pattern = {"files": ["*.csproj"], "dirs": [], "extensions": []}
        result = await detector._check_patterns(temp_dir, pattern)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_check_patterns_with_directories(self, detector, temp_dir):
        """Test pattern checking with directory patterns."""
        # Create directory structure
        (temp_dir / "node_modules").mkdir()
        
        pattern = {"files": [], "dirs": ["node_modules"], "extensions": []}
        result = await detector._check_patterns(temp_dir, pattern)
        
        assert result is True 