"""Core gitignore generation functionality."""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional

import aiohttp
import git
from rich.console import Console

from .exceptions import APIError, GitError, TemplateError
from .utils import backup_file, get_cache_dir, get_common_security_patterns, merge_gitignore_content

console = Console()


class GitignoreGenerator:
    """Main class for generating .gitignore files."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.cache_dir = get_cache_dir()
        self.api_base_url = "https://www.tgitignore.io/api"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def generate(
        self,
        technologies: List[str],
        security_patterns: bool = False,
        monorepo: bool = False,
        minimal: bool = False,
        strict: bool = False,
    ) -> str:
        """Generate .gitignore content for the given technologies."""
        try:
            self.logger.info(f"Generating .gitignore for technologies: {technologies}")
            
            # Fetch templates
            templates = []
            for tech in technologies:
                template = await self._fetch_template(tech)
                if template:
                    templates.append(template)
            
            if not templates:
                raise TemplateError("No templates could be fetched")
            
            # Merge templates
            merged_content = self._merge_templates(templates)
            
            # Apply minimal mode if requested
            if minimal:
                merged_content = self._minimize_content(merged_content)
            
            # Apply strict mode if requested
            if strict:
                merged_content = self._apply_strict_patterns(merged_content)
            
            # Add security patterns if requested
            if security_patterns:
                security_content = "\n".join(get_common_security_patterns())
                merged_content = merge_gitignore_content(merged_content, security_content)
            
            # Add header
            header = self._generate_header(technologies)
            final_content = f"{header}\n\n{merged_content}"
            
            return final_content
            
        except Exception as e:
            raise TemplateError(f"Failed to generate .gitignore: {e}")

    async def auto_fix_ignored_files(self, repo_path: Path) -> List[str]:
        """Automatically remove files that should be ignored from git tracking."""
        try:
            ignored_files = await self.check_git_status(repo_path)
            
            if not ignored_files:
                return []
            
            # Remove files from git tracking
            import git
            repo = git.Repo(repo_path)
            
            removed_files = []
            for file_path in ignored_files:
                try:
                    repo.index.remove([file_path], working_tree=True)
                    removed_files.append(file_path)
                    self.logger.info(f"Removed from git tracking: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove {file_path}: {e}")
            
            return removed_files
            
        except Exception as e:
            raise GitError(f"Failed to auto-fix ignored files: {e}")

    def _minimize_content(self, content: str) -> str:
        """Minimize .gitignore content to only essential patterns."""
        essential_patterns = [
            "*.log",
            ".env*",
            "__pycache__/",
            "node_modules/",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".DS_Store",
            "Thumbs.db",
            "*.tmp",
            "*.temp",
            ".cache/",
            "dist/",
            "build/",
            "*.egg-info/",
        ]
        
        lines = content.splitlines()
        minimal_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Keep essential patterns
            if any(pattern in line for pattern in essential_patterns):
                minimal_lines.append(line)
        
        return "\n".join(minimal_lines)

    def _apply_strict_patterns(self, content: str) -> str:
        """Apply stricter pattern matching for better accuracy."""
        lines = content.splitlines()
        strict_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                strict_lines.append(line)
                continue
            
            # Make patterns more specific
            if line.endswith("/"):
                # Directory patterns - keep as is
                strict_lines.append(line)
            elif line.startswith("*."):
                # File extension patterns - keep as is
                strict_lines.append(line)
            elif line.startswith("/"):
                # Absolute paths - keep as is
                strict_lines.append(line)
            else:
                # Relative patterns - make more specific
                strict_lines.append(f"**/{line}")
        
        return "\n".join(strict_lines)

    async def export_config(self, file_path: Path) -> None:
        """Export current .gitignore configuration."""
        try:
            config = {
                "version": "1.0",
                "generated_at": asyncio.get_event_loop().time(),
                "gitignore_path": str(file_path),
                "content": file_path.read_text() if file_path.exists() else "",
            }
            
            import json
            config_file = file_path.parent / ".gitignore-gen.json"
            config_file.write_text(json.dumps(config, indent=2))
            
            self.logger.info(f"Configuration exported to: {config_file}")
            
        except Exception as e:
            raise TemplateError(f"Failed to export configuration: {e}")

    async def import_config(self, config_file: Path) -> str:
        """Import .gitignore configuration."""
        try:
            import json
            config = json.loads(config_file.read_text())
            
            if "content" in config:
                return config["content"]
            else:
                raise TemplateError("Invalid configuration file format")
                
        except Exception as e:
            raise TemplateError(f"Failed to import configuration: {e}")

    async def get_custom_templates(self) -> dict[str, str]:
        """Get custom templates from the cache directory."""
        try:
            from .utils import get_cache_dir
            templates_dir = get_cache_dir() / "custom_templates"
            
            if not templates_dir.exists():
                return {}
            
            templates = {}
            for template_file in templates_dir.glob("*.gitignore"):
                template_name = template_file.stem
                templates[template_name] = template_file.read_text()
            
            return templates
            
        except Exception as e:
            self.logger.warning(f"Failed to load custom templates: {e}")
            return {}

    async def _fetch_template(self, technology: str) -> Optional[str]:
        """Fetch template from gitignore.io API."""
        try:
            # Check cache first
            cache_file = self.cache_dir / f"{technology}.gitignore"
            if cache_file.exists():
                self.logger.debug(f"Using cached template for {technology}")
                return cache_file.read_text()
            
            # Fetch from API
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.api_base_url}/{technology}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Cache the template
                    cache_file.write_text(content)
                    
                    return content
                else:
                    self.logger.warning(f"Failed to fetch template for {technology}: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.warning(f"Error fetching template for {technology}: {e}")
            return self._get_fallback_template(technology)

    def _get_fallback_template(self, technology: str) -> Optional[str]:
        """Get fallback template from bundled templates."""
        # Common fallback templates
        fallback_templates = {
            "python": """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/
""",
            "node": """# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# Diagnostic reports (https://nodejs.org/api/report.html)
report.[0-9]*.[0-9]*.[0-9]*.[0-9]*.json

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Directory for instrumented libs generated by jscoverage/JSCover
lib-cov

# Coverage directory used by tools like istanbul
coverage
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage (https://gruntjs.com/creating-plugins#storing-task-files)
.grunt

# Bower dependency directory (https://bower.io/)
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons (https://nodejs.org/api/addons.html)
build/Release

# Dependency directories
node_modules/
jspm_packages/

# Snowpack dependency directory (https://snowpack.dev/)
web_modules/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Optional stylelint cache
.stylelintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variable files
.env
.env.development.local
.env.test.local
.env.production.local
.env.local

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# Next.js build output
.next
out

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
public

# Vuepress build output
.vuepress/dist

# Serverless directories
.serverless/

# FuseBox cache
.fusebox/

# DynamoDB Local files
.dynamodb/

# TernJS port file
.tern-port

# Stores VSCode versions used for testing VSCode extensions
.vscode-test

# yarn v2
.yarn/cache
.yarn/unplugged
.yarn/build-state.yml
.yarn/install-state.gz
.pnp.*
""",
            "java": """# Compiled class file
*.class

# Log file
*.log

# BlueJ files
*.ctxt

# Mobile Tools for Java (J2ME)
.mtj.tmp/

# Package Files #
*.jar
*.war
*.nar
*.ear
*.zip
*.tar.gz
*.rar

# virtual machine crash logs, see http://www.java.com/en/download/help/error_hotspot.xml
hs_err_pid*
replay_pid*

# Maven
target/
pom.xml.tag
pom.xml.releaseBackup
pom.xml.versionsBackup
pom.xml.next
release.properties
dependency-reduced-pom.xml
buildNumber.properties
.mvn/timing.properties
.mvn/wrapper/maven-wrapper.jar

# Gradle
.gradle
build/

# IntelliJ IDEA
.idea/
*.iws
*.iml
*.ipr

# Eclipse
.apt_generated
.classpath
.factorypath
.project
.settings
.springBeans
.sts4-cache

# NetBeans
/nbproject/private/
/nbbuild/
/dist/
/nbdist/
/.nb-gradle/
build/
!**/src/main/**/build/
!**/src/test/**/build/

# VS Code
.vscode/
""",
        }
        
        return fallback_templates.get(technology.lower())

    def _merge_templates(self, templates: List[str]) -> str:
        """Merge multiple templates, removing duplicates."""
        if not templates:
            return ""
        
        if len(templates) == 1:
            return templates[0]
        
        # Start with the first template
        merged = templates[0]
        
        # Merge with remaining templates
        for template in templates[1:]:
            merged = merge_gitignore_content(merged, template)
        
        return merged

    def _generate_header(self, technologies: List[str]) -> str:
        """Generate a header for the .gitignore file."""
        tech_list = ", ".join(technologies)
        return f"""# Generated by gitignore-gen
# Technologies detected: {tech_list}
# Generated on: {asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 'unknown'}

# This file was automatically generated by gitignore-gen
# Visit: https://github.com/your-username/gitignore-gen for more information"""

    async def save_gitignore(
        self, file_path: Path, content: str, backup: bool = False
    ) -> None:
        """Save the .gitignore file."""
        try:
            # Create backup if requested
            if backup and file_path.exists():
                backup_path = backup_file(file_path)
                self.logger.info(f"Created backup: {backup_path}")
            
            # Write the file
            file_path.write_text(content)
            self.logger.info(f"Saved .gitignore to: {file_path}")
            
        except Exception as e:
            raise TemplateError(f"Failed to save .gitignore: {e}")

    async def check_git_status(self, repo_path: Path) -> List[str]:
        """Check for files that should be ignored but are tracked in git."""
        try:
            repo = git.Repo(repo_path)
            
            # Get all tracked files
            tracked_files = []
            for item in repo.index.iter_blobs():
                tracked_files.append(item[1].path)  # item is a tuple, second element is the Blob object
            
            # Read .gitignore content
            gitignore_path = repo_path / ".gitignore"
            if not gitignore_path.exists():
                return []
            
            gitignore_content = gitignore_path.read_text()
            
            # Check which tracked files should be ignored
            ignored_files = []
            for file_path in tracked_files:
                if self._should_be_ignored(file_path, gitignore_content):
                    ignored_files.append(file_path)
            
            return ignored_files
            
        except git.InvalidGitRepositoryError:
            self.logger.warning("Not a git repository")
            return []
        except Exception as e:
            raise GitError(f"Failed to check git status: {e}")

    def _should_be_ignored(self, file_path: str, gitignore_content: str) -> bool:
        """Check if a file should be ignored based on .gitignore content."""
        # Simple implementation - in production, you'd want to use pathspec
        lines = gitignore_content.splitlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Convert pattern to regex and check
            if self._matches_pattern(file_path, line):
                return True
        
        return False

    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if a file path matches a gitignore pattern."""
        # Simple pattern matching - in production, use pathspec
        import fnmatch
        
        return fnmatch.fnmatch(file_path, pattern) 