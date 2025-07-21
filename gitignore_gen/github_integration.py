"""GitHub integration for gitignore-gen."""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse

import aiohttp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class GitHubIntegration:
    """GitHub integration for repository analysis and insights."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.api_base = "https://api.github.com"
        self.headers = {}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        
        self.cache_dir = Path.home() / ".gign" / "github_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    async def analyze_repository(self, repo_url: str) -> Dict:
        """Analyze a GitHub repository and extract .gitignore patterns."""
        try:
            # Parse repository URL
            repo_info = self._parse_repo_url(repo_url)
            if not repo_info:
                raise ValueError("Invalid GitHub repository URL")
            
            owner, repo = repo_info
            
            # Get repository information
            repo_data = await self._get_repository_data(owner, repo)
            
            # Get .gitignore file
            gitignore_content = await self._get_gitignore_file(owner, repo)
            
            # Analyze repository structure
            structure_analysis = await self._analyze_repository_structure(owner, repo)
            
            # Get language statistics
            languages = await self._get_language_stats(owner, repo)
            
            return {
                "repository": repo_data,
                "gitignore_content": gitignore_content,
                "structure_analysis": structure_analysis,
                "languages": languages,
                "recommendations": await self._generate_repo_recommendations(
                    gitignore_content, languages, structure_analysis
                )
            }
            
        except Exception as e:
            console.print(f"[red]Error analyzing repository: {e}[/red]")
            return {}
    
    def _parse_repo_url(self, repo_url: str) -> Optional[Tuple[str, str]]:
        """Parse GitHub repository URL to extract owner and repo name."""
        try:
            parsed = urlparse(repo_url)
            if "github.com" in parsed.netloc:
                path_parts = parsed.path.strip("/").split("/")
                if len(path_parts) >= 2:
                    return path_parts[0], path_parts[1]
        except Exception:
            pass
        return None
    
    async def _get_repository_data(self, owner: str, repo: str) -> Dict:
        """Get basic repository information."""
        url = f"{self.api_base}/repos/{owner}/{repo}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get repository data: {response.status}")
    
    async def _get_gitignore_file(self, owner: str, repo: str) -> Optional[str]:
        """Get .gitignore file content from repository."""
        url = f"{self.api_base}/repos/{owner}/{repo}/contents/.gitignore"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if "content" in data:
                        import base64
                        return base64.b64decode(data["content"]).decode("utf-8")
                return None
    
    async def _analyze_repository_structure(self, owner: str, repo: str) -> Dict:
        """Analyze repository file structure."""
        url = f"{self.api_base}/repos/{owner}/{repo}/contents"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    contents = await response.json()
                    
                    analysis = {
                        "files": [],
                        "directories": [],
                        "file_types": {},
                        "has_package_files": False,
                        "has_config_files": False
                    }
                    
                    for item in contents:
                        if item["type"] == "file":
                            analysis["files"].append(item["name"])
                            
                            # Analyze file types
                            ext = Path(item["name"]).suffix.lower()
                            if ext:
                                analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
                            
                            # Check for package files
                            if item["name"] in ["package.json", "requirements.txt", "pyproject.toml", "Cargo.toml"]:
                                analysis["has_package_files"] = True
                            
                            # Check for config files
                            if "config" in item["name"].lower() or item["name"].startswith("."):
                                analysis["has_config_files"] = True
                                
                        elif item["type"] == "dir":
                            analysis["directories"].append(item["name"])
                    
                    return analysis
                else:
                    return {}
    
    async def _get_language_stats(self, owner: str, repo: str) -> Dict:
        """Get repository language statistics."""
        url = f"{self.api_base}/repos/{owner}/{repo}/languages"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
    
    async def _generate_repo_recommendations(
        self, 
        gitignore_content: Optional[str], 
        languages: Dict, 
        structure: Dict
    ) -> List[Dict]:
        """Generate recommendations based on repository analysis."""
        recommendations = []
        
        # Check if .gitignore exists
        if not gitignore_content:
            recommendations.append({
                "type": "missing_gitignore",
                "priority": "high",
                "message": "Repository doesn't have a .gitignore file",
                "action": "Create a .gitignore file based on detected technologies"
            })
        
        # Language-specific recommendations
        for lang, bytes_count in languages.items():
            if lang.lower() == "python":
                if not gitignore_content or "__pycache__" not in gitignore_content:
                    recommendations.append({
                        "type": "python_patterns",
                        "priority": "medium",
                        "message": "Missing Python-specific patterns",
                        "action": "Add __pycache__/, *.pyc, .pytest_cache/ patterns"
                    })
            
            elif lang.lower() == "javascript":
                if not gitignore_content or "node_modules" not in gitignore_content:
                    recommendations.append({
                        "type": "node_patterns",
                        "priority": "medium",
                        "message": "Missing Node.js-specific patterns",
                        "action": "Add node_modules/, npm-debug.log* patterns"
                    })
        
        # Structure-based recommendations
        if structure.get("has_config_files") and not gitignore_content:
            recommendations.append({
                "type": "config_files",
                "priority": "medium",
                "message": "Repository has config files",
                "action": "Consider adding config files to .gitignore if they contain secrets"
            })
        
        return recommendations
    
    async def get_trending_repositories(self, language: Optional[str] = None) -> List[Dict]:
        """Get trending repositories for analysis."""
        url = f"{self.api_base}/search/repositories"
        params = {
            "q": "stars:>100",
            "sort": "stars",
            "order": "desc",
            "per_page": 10
        }
        
        if language:
            params["q"] += f" language:{language}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                else:
                    return []
    
    async def analyze_multiple_repositories(self, repo_urls: List[str]) -> Dict:
        """Analyze multiple repositories and find common patterns."""
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing repositories...", total=len(repo_urls))
            
            for repo_url in repo_urls:
                progress.update(task, description=f"Analyzing {repo_url}")
                result = await self.analyze_repository(repo_url)
                if result:
                    results.append(result)
                progress.advance(task)
        
        # Find common patterns
        common_patterns = self._find_common_patterns(results)
        
        return {
            "repositories": results,
            "common_patterns": common_patterns,
            "recommendations": self._generate_common_recommendations(results)
        }
    
    def _find_common_patterns(self, results: List[Dict]) -> Dict[str, int]:
        """Find common .gitignore patterns across repositories."""
        pattern_counts = {}
        
        for result in results:
            gitignore_content = result.get("gitignore_content", "")
            if gitignore_content:
                lines = gitignore_content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        pattern_counts[line] = pattern_counts.get(line, 0) + 1
        
        # Sort by frequency
        return dict(sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _generate_common_recommendations(self, results: List[Dict]) -> List[Dict]:
        """Generate recommendations based on common patterns."""
        recommendations = []
        
        # Count missing .gitignore files
        missing_gitignore = sum(1 for r in results if not r.get("gitignore_content"))
        if missing_gitignore > 0:
            recommendations.append({
                "type": "missing_gitignore",
                "count": missing_gitignore,
                "percentage": (missing_gitignore / len(results)) * 100,
                "message": f"{missing_gitignore} repositories missing .gitignore files"
            })
        
        # Find most common languages
        all_languages = {}
        for result in results:
            languages = result.get("languages", {})
            for lang, bytes_count in languages.items():
                all_languages[lang] = all_languages.get(lang, 0) + bytes_count
        
        top_languages = sorted(all_languages.items(), key=lambda x: x[1], reverse=True)[:5]
        
        recommendations.append({
            "type": "top_languages",
            "languages": top_languages,
            "message": "Most common languages in analyzed repositories"
        })
        
        return recommendations
    
    def display_repository_analysis(self, analysis: Dict) -> None:
        """Display repository analysis results."""
        if not analysis:
            console.print("[red]No analysis data available[/red]")
            return
        
        repo_data = analysis.get("repository", {})
        gitignore_content = analysis.get("gitignore_content")
        languages = analysis.get("languages", {})
        recommendations = analysis.get("recommendations", [])
        
        # Repository info
        console.print(Panel(
            f"[bold blue]{repo_data.get('full_name', 'Unknown')}[/bold blue]\n"
            f"[dim]{repo_data.get('description', 'No description')}[/dim]\n"
            f"⭐ {repo_data.get('stargazers_count', 0)} stars | "
            f"🔀 {repo_data.get('forks_count', 0)} forks | "
            f"👀 {repo_data.get('watchers_count', 0)} watchers",
            title="📊 Repository Information"
        ))
        
        # Languages
        if languages:
            lang_table = Table(title="🔤 Languages")
            lang_table.add_column("Language", style="cyan")
            lang_table.add_column("Bytes", style="green")
            lang_table.add_column("Percentage", style="yellow")
            
            total_bytes = sum(languages.values())
            for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                percentage = (bytes_count / total_bytes) * 100
                lang_table.add_row(lang, f"{bytes_count:,}", f"{percentage:.1f}%")
            
            console.print(lang_table)
        
        # .gitignore status
        if gitignore_content:
            lines = len(gitignore_content.split("\n"))
            console.print(f"✅ .gitignore file found ({lines} lines)")
        else:
            console.print("❌ No .gitignore file found")
        
        # Recommendations
        if recommendations:
            rec_table = Table(title="💡 Recommendations")
            rec_table.add_column("Priority", style="bold")
            rec_table.add_column("Message", style="white")
            rec_table.add_column("Action", style="yellow")
            
            for rec in recommendations:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec["priority"], "⚪")
                rec_table.add_row(
                    f"{priority_emoji} {rec['priority'].title()}",
                    rec["message"],
                    rec["action"]
                )
            
            console.print(rec_table)
    
    def display_common_patterns(self, patterns: Dict[str, int]) -> None:
        """Display common patterns found across repositories."""
        if not patterns:
            console.print("No common patterns found")
            return
        
        table = Table(title="🔍 Common .gitignore Patterns")
        table.add_column("Pattern", style="cyan")
        table.add_column("Frequency", style="green")
        table.add_column("Percentage", style="yellow")
        
        max_count = max(patterns.values())
        for pattern, count in list(patterns.items())[:20]:  # Top 20
            percentage = (count / max_count) * 100
            table.add_row(pattern, str(count), f"{percentage:.1f}%")
        
        console.print(table)


class RepositorySync:
    """Sync local .gitignore with GitHub repository."""
    
    def __init__(self, token: Optional[str] = None):
        self.github = GitHubIntegration(token)
    
    async def sync_to_github(
        self, 
        local_path: Path, 
        repo_url: str, 
        commit_message: str = "Update .gitignore via gign"
    ) -> bool:
        """Sync local .gitignore to GitHub repository."""
        try:
            # Parse repository URL
            repo_info = self.github._parse_repo_url(repo_url)
            if not repo_info:
                raise ValueError("Invalid GitHub repository URL")
            
            owner, repo = repo_info
            
            # Read local .gitignore
            gitignore_path = local_path / ".gitignore"
            if not gitignore_path.exists():
                raise FileNotFoundError("No .gitignore file found locally")
            
            content = gitignore_path.read_text()
            
            # Get current .gitignore from GitHub
            current_gitignore = await self.github._get_gitignore_file(owner, repo)
            
            if current_gitignore == content:
                console.print("✅ .gitignore is already up to date")
                return True
            
            # Update .gitignore on GitHub
            await self._update_gitignore_file(owner, repo, content, commit_message)
            
            console.print("✅ .gitignore synced to GitHub successfully")
            return True
            
        except Exception as e:
            console.print(f"[red]Error syncing to GitHub: {e}[/red]")
            return False
    
    async def _update_gitignore_file(
        self, 
        owner: str, 
        repo: str, 
        content: str, 
        commit_message: str
    ) -> None:
        """Update .gitignore file on GitHub."""
        url = f"{self.github.api_base}/repos/{owner}/{repo}/contents/.gitignore"
        
        # Get current file SHA
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.github.headers) as response:
                if response.status == 200:
                    current_data = await response.json()
                    sha = current_data["sha"]
                else:
                    sha = None
        
        # Prepare update data
        import base64
        data = {
            "message": commit_message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": "main"  # You might want to make this configurable
        }
        
        if sha:
            data["sha"] = sha
        
        # Update file
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=self.github.headers, json=data) as response:
                if response.status not in [200, 201]:
                    raise Exception(f"Failed to update .gitignore: {response.status}")


# Global instances
github_integration = GitHubIntegration()
repository_sync = RepositorySync() 