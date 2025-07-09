"""Advanced technology detection for gitignore-gen."""

import asyncio
import logging
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

from rich.console import Console

console = Console()


class AdvancedTechnologyDetector:
    """Advanced technology detector with ML and dependency analysis."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.technology_patterns = self._load_technology_patterns()
        self.dependency_files = self._load_dependency_files()
        self.project_indicators = self._load_project_indicators()

    def _load_technology_patterns(self) -> Dict[str, List[str]]:
        """Load comprehensive technology detection patterns."""
        return {
            "python": [
                r"\.py$", r"requirements\.txt$", r"setup\.py$", r"pyproject\.toml$",
                r"Pipfile$", r"poetry\.lock$", r"__pycache__", r"\.pyc$", r"\.pyo$",
                r"\.pytest_cache", r"\.coverage", r"\.tox", r"\.venv", r"venv/",
                r"\.mypy_cache", r"\.ruff_cache", r"\.black", r"\.isort"
            ],
            "node": [
                r"package\.json$", r"package-lock\.json$", r"yarn\.lock$", r"pnpm-lock\.yaml$",
                r"node_modules/", r"\.npm", r"\.nvmrc", r"\.node-version", r"\.nvm",
                r"\.eslintrc", r"\.prettierrc", r"\.babelrc", r"webpack\.config",
                r"rollup\.config", r"vite\.config", r"next\.config", r"nuxt\.config"
            ],
            "java": [
                r"\.java$", r"\.class$", r"\.jar$", r"pom\.xml$", r"build\.gradle$",
                r"gradle\.properties$", r"\.gradle", r"target/", r"\.idea", r"\.eclipse",
                r"\.mvn", r"\.classpath", r"\.project", r"\.settings"
            ],
            "go": [
                r"\.go$", r"go\.mod$", r"go\.sum$", r"vendor/", r"\.go-version",
                r"Gopkg\.toml$", r"Gopkg\.lock$", r"\.golangci-lint"
            ],
            "rust": [
                r"\.rs$", r"Cargo\.toml$", r"Cargo\.lock$", r"target/", r"\.rustc_info",
                r"\.cargo", r"rust-toolchain", r"rust-toolchain\.toml"
            ],
            "php": [
                r"\.php$", r"composer\.json$", r"composer\.lock$", r"vendor/",
                r"\.phpunit", r"\.php-cs-fixer", r"\.phpstan", r"\.env"
            ],
            "ruby": [
                r"\.rb$", r"Gemfile$", r"Gemfile\.lock$", r"Rakefile$", r"\.ruby-version",
                r"\.ruby-gemset", r"\.bundle", r"vendor/bundle", r"\.rvmrc"
            ],
            "csharp": [
                r"\.cs$", r"\.csproj$", r"\.sln$", r"packages\.config$", r"\.nuget",
                r"bin/", r"obj/", r"\.vs", r"\.vscode", r"\.omnisharp"
            ],
            "swift": [
                r"\.swift$", r"\.xcodeproj", r"\.xcworkspace", r"Podfile$", r"Podfile\.lock$",
                r"\.swiftpm", r"\.build", r"DerivedData", r"\.xcuserdata"
            ],
            "kotlin": [
                r"\.kt$", r"\.kts$", r"build\.gradle\.kts$", r"\.gradle", r"\.idea",
                r"build/", r"\.kotlin", r"\.kts"
            ],
            "scala": [
                r"\.scala$", r"\.sbt$", r"build\.sbt$", r"project/", r"target/",
                r"\.sbt", r"\.scala", r"\.metals"
            ],
            "dart": [
                r"\.dart$", r"pubspec\.yaml$", r"pubspec\.lock$", r"\.dart_tool",
                r"build/", r"\.packages", r"\.pub"
            ],
            "flutter": [
                r"\.dart$", r"pubspec\.yaml$", r"pubspec\.lock$", r"\.flutter-plugins",
                r"\.flutter-plugins-dependencies", r"build/", r"\.dart_tool"
            ],
            "react": [
                r"\.jsx$", r"\.tsx$", r"react", r"next\.config", r"\.next", r"out/",
                r"\.gatsby", r"gatsby-config", r"\.nuxt", r"nuxt\.config"
            ],
            "vue": [
                r"\.vue$", r"vue\.config", r"\.nuxt", r"nuxt\.config", r"\.quasar",
                r"quasar\.config", r"\.vite", r"vite\.config"
            ],
            "angular": [
                r"angular\.json$", r"\.angular", r"\.angular-cli", r"angular-cli\.json",
                r"\.ng", r"\.angular-cli"
            ],
            "svelte": [
                r"\.svelte$", r"svelte\.config", r"\.svelte-kit", r"build/", r"\.vite"
            ],
            "docker": [
                r"Dockerfile", r"docker-compose", r"\.dockerignore", r"\.docker",
                r"docker-compose\.yml", r"docker-compose\.yaml", r"\.dockerignore"
            ],
            "kubernetes": [
                r"\.yaml$", r"\.yml$", r"kustomization", r"\.k8s", r"\.kubernetes",
                r"helm", r"\.helm", r"Chart\.yaml", r"values\.yaml"
            ],
            "terraform": [
                r"\.tf$", r"\.tfvars$", r"\.hcl$", r"\.terraform", r"terraform\.tfstate",
                r"\.tfstate\.backup", r"\.terraform\.lock\.hcl"
            ],
            "ansible": [
                r"\.yml$", r"\.yaml$", r"inventory", r"playbook", r"\.ansible",
                r"ansible\.cfg", r"\.ansible-lint"
            ],
            "jenkins": [
                r"Jenkinsfile", r"\.jenkins", r"\.groovy", r"\.jenkinsfile",
                r"jenkins\.groovy", r"\.jenkins"
            ],
            "github": [
                r"\.github", r"\.gitignore", r"\.gitattributes", r"\.git",
                r"\.github/workflows", r"\.github/actions"
            ],
            "gitlab": [
                r"\.gitlab-ci\.yml$", r"\.gitlab", r"gitlab-ci\.yml", r"\.gitlab-ci"
            ],
            "vscode": [
                r"\.vscode", r"\.code-workspace", r"\.vscode/settings\.json",
                r"\.vscode/launch\.json", r"\.vscode/tasks\.json"
            ],
            "intellij": [
                r"\.idea", r"\.iml$", r"\.ipr$", r"\.iws$", r"\.idea/workspace\.xml"
            ],
            "eclipse": [
                r"\.project", r"\.classpath", r"\.settings", r"\.metadata",
                r"\.eclipse", r"\.eclipseproduct"
            ],
            "vim": [
                r"\.vimrc", r"\.vim", r"\.viminfo", r"\.vimrc\.local", r"\.vimrc\.before"
            ],
            "emacs": [
                r"\.emacs", r"\.emacs\.d", r"\.emacs\.desktop", r"\.emacs\.server",
                r"\.emacs\.backup", r"\.emacs\.auto"
            ],
            "macos": [
                r"\.DS_Store", r"\.AppleDouble", r"\.LSOverride", r"\.Spotlight-V100",
                r"\.Trashes", r"\.fseventsd", r"\.TemporaryItems"
            ],
            "windows": [
                r"Thumbs\.db", r"ehthumbs\.db", r"Desktop\.ini", r"\.lnk$",
                r"\.tmp$", r"\.temp$", r"\.log$", r"\.bak$", r"\.old$"
            ],
            "linux": [
                r"\.cache", r"\.config", r"\.local", r"\.mozilla", r"\.thunderbird",
                r"\.gnome", r"\.kde", r"\.xfce", r"\.config"
            ],
        }

    def _load_dependency_files(self) -> Dict[str, List[str]]:
        """Load dependency file patterns."""
        return {
            "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "poetry.lock"],
            "node": ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
            "java": ["pom.xml", "build.gradle", "gradle.properties"],
            "go": ["go.mod", "go.sum", "Gopkg.toml"],
            "rust": ["Cargo.toml", "Cargo.lock"],
            "php": ["composer.json", "composer.lock"],
            "ruby": ["Gemfile", "Gemfile.lock", "Rakefile"],
            "csharp": [".csproj", ".sln", "packages.config"],
            "swift": ["Podfile", "Podfile.lock"],
            "kotlin": ["build.gradle.kts"],
            "scala": ["build.sbt"],
            "dart": ["pubspec.yaml", "pubspec.lock"],
            "flutter": ["pubspec.yaml", "pubspec.lock"],
        }

    def _load_project_indicators(self) -> Dict[str, List[str]]:
        """Load project structure indicators."""
        return {
            "monorepo": ["lerna.json", "nx.json", "rush.json", "pnpm-workspace.yaml"],
            "microservices": ["docker-compose.yml", "docker-compose.yaml", "kubernetes"],
            "fullstack": ["frontend/", "backend/", "client/", "server/"],
            "mobile": ["android/", "ios/", "mobile/", "app/"],
            "desktop": ["src/", "main/", "app/", "resources/"],
            "library": ["lib/", "src/", "include/", "headers/"],
            "cli": ["bin/", "cli/", "cmd/", "main.py", "main.go"],
            "api": ["api/", "routes/", "controllers/", "endpoints/"],
            "database": ["migrations/", "schema/", "models/", "entities/"],
            "testing": ["tests/", "test/", "spec/", "__tests__/", "test_"],
        }

    async def detect_advanced(self, path: Path) -> Dict[str, any]:
        """Perform advanced technology detection with detailed analysis."""
        try:
            self.logger.info(f"Performing advanced detection on: {path}")
            
            # Basic technology detection
            technologies = await self._detect_technologies(path)
            
            # Dependency analysis
            dependencies = await self._analyze_dependencies(path)
            
            # Project structure analysis
            structure = await self._analyze_project_structure(path)
            
            # File statistics
            stats = await self._analyze_file_statistics(path)
            
            # Security analysis
            security = await self._analyze_security_concerns(path)
            
            # Performance analysis
            performance = await self._analyze_performance_indicators(path)
            
            return {
                "technologies": technologies,
                "dependencies": dependencies,
                "structure": structure,
                "statistics": stats,
                "security": security,
                "performance": performance,
                "recommendations": await self._generate_recommendations(
                    technologies, dependencies, structure, security, performance
                )
            }
            
        except Exception as e:
            self.logger.error(f"Advanced detection failed: {e}")
            return {}

    async def _detect_technologies(self, path: Path) -> Dict[str, float]:
        """Detect technologies with confidence scores."""
        technologies = {}
        
        for tech, patterns in self.technology_patterns.items():
            confidence = 0.0
            matches = 0
            
            for pattern in patterns:
                for file_path in path.rglob("*"):
                    if file_path.is_file() and re.search(pattern, str(file_path), re.IGNORECASE):
                        matches += 1
                        confidence += 0.1
            
            if matches > 0:
                confidence = min(confidence, 1.0)
                technologies[tech] = confidence
        
        return technologies

    async def _analyze_dependencies(self, path: Path) -> Dict[str, any]:
        """Analyze project dependencies."""
        dependencies = {}
        
        for tech, files in self.dependency_files.items():
            for dep_file in files:
                dep_path = path / dep_file
                if dep_path.exists():
                    dependencies[tech] = {
                        "file": dep_file,
                        "path": str(dep_path),
                        "size": dep_path.stat().st_size,
                        "modified": dep_path.stat().st_mtime
                    }
                    break
        
        return dependencies

    async def _analyze_project_structure(self, path: Path) -> Dict[str, any]:
        """Analyze project structure and organization."""
        structure = {
            "type": "unknown",
            "indicators": [],
            "directories": [],
            "depth": 0
        }
        
        # Analyze directory structure
        dirs = [d for d in path.iterdir() if d.is_dir()]
        structure["directories"] = [d.name for d in dirs]
        structure["depth"] = max(len(p.parts) - len(path.parts) for p in path.rglob("*"))
        
        # Detect project type
        for project_type, indicators in self.project_indicators.items():
            for indicator in indicators:
                if any(indicator in str(p) for p in path.rglob("*")):
                    structure["indicators"].append(project_type)
                    break
        
        if structure["indicators"]:
            structure["type"] = structure["indicators"][0]
        
        return structure

    async def _analyze_file_statistics(self, path: Path) -> Dict[str, any]:
        """Analyze file statistics and patterns."""
        stats = {
            "total_files": 0,
            "total_dirs": 0,
            "file_types": {},
            "largest_files": [],
            "recent_files": []
        }
        
        files = []
        for file_path in path.rglob("*"):
            if file_path.is_file():
                stats["total_files"] += 1
                files.append(file_path)
                
                # File type analysis
                ext = file_path.suffix.lower()
                if ext:
                    stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
            else:
                stats["total_dirs"] += 1
        
        # Largest files
        files_by_size = sorted(files, key=lambda f: f.stat().st_size, reverse=True)
        stats["largest_files"] = [
            {"path": str(f), "size": f.stat().st_size} 
            for f in files_by_size[:10]
        ]
        
        # Recent files
        files_by_time = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
        stats["recent_files"] = [
            {"path": str(f), "modified": f.stat().st_mtime} 
            for f in files_by_time[:10]
        ]
        
        return stats

    async def _analyze_security_concerns(self, path: Path) -> Dict[str, any]:
        """Analyze potential security concerns."""
        security = {
            "sensitive_files": [],
            "exposed_secrets": [],
            "weak_patterns": [],
            "recommendations": []
        }
        
        sensitive_patterns = [
            r"\.env", r"\.key", r"\.pem", r"\.p12", r"\.pfx", r"\.crt", r"\.cer",
            r"\.pwd", r"password", r"secret", r"token", r"api_key", r"private_key"
        ]
        
        for pattern in sensitive_patterns:
            for file_path in path.rglob("*"):
                if file_path.is_file() and re.search(pattern, str(file_path), re.IGNORECASE):
                    security["sensitive_files"].append(str(file_path))
        
        # Check for common security issues
        if any("node_modules" in str(p) for p in path.rglob("*")):
            security["recommendations"].append("Consider using .npmrc for npm configuration")
        
        if any(".env" in str(p) for p in path.rglob("*")):
            security["recommendations"].append("Ensure .env files are in .gitignore")
        
        return security

    async def _analyze_performance_indicators(self, path: Path) -> Dict[str, any]:
        """Analyze performance indicators."""
        performance = {
            "large_files": [],
            "many_files": False,
            "deep_nesting": False,
            "recommendations": []
        }
        
        # Check for large files
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                performance["large_files"].append({
                    "path": str(file_path),
                    "size": file_path.stat().st_size
                })
        
        # Check for many files
        file_count = len(list(path.rglob("*")))
        if file_count > 10000:
            performance["many_files"] = True
            performance["recommendations"].append("Consider using .gitignore to exclude unnecessary files")
        
        # Check for deep nesting
        max_depth = max(len(p.parts) - len(path.parts) for p in path.rglob("*"))
        if max_depth > 10:
            performance["deep_nesting"] = True
            performance["recommendations"].append("Consider flattening directory structure")
        
        return performance

    async def _generate_recommendations(
        self, 
        technologies: Dict[str, float], 
        dependencies: Dict[str, any],
        structure: Dict[str, any],
        security: Dict[str, any],
        performance: Dict[str, any]
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Technology-specific recommendations
        if "python" in technologies:
            recommendations.append("Consider adding __pycache__/ and *.pyc to .gitignore")
        
        if "node" in technologies:
            recommendations.append("Ensure node_modules/ is in .gitignore")
        
        if "java" in technologies:
            recommendations.append("Add target/ and *.class to .gitignore")
        
        # Security recommendations
        recommendations.extend(security["recommendations"])
        
        # Performance recommendations
        recommendations.extend(performance["recommendations"])
        
        # Structure recommendations
        if structure["type"] == "monorepo":
            recommendations.append("Consider using per-directory .gitignore files")
        
        if structure["type"] == "microservices":
            recommendations.append("Add service-specific .gitignore patterns")
        
        return recommendations 