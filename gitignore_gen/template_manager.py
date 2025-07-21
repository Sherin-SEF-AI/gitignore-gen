"""Advanced template management for gitignore-gen."""

import asyncio
import json
import logging
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import zipfile
import tempfile

import aiohttp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@dataclass
class Template:
    """Template metadata and content."""
    name: str
    description: str
    content: str
    author: str
    version: str
    tags: List[str]
    technologies: List[str]
    created_at: datetime
    updated_at: datetime
    downloads: int
    rating: float
    is_official: bool
    is_custom: bool
    file_size: int
    checksum: str


class TemplateManager:
    """Advanced template management system."""
    
    def __init__(self):
        self.templates_dir = Path.home() / ".gign" / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.custom_dir = self.templates_dir / "custom"
        self.custom_dir.mkdir(exist_ok=True)
        
        self.community_dir = self.templates_dir / "community"
        self.community_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.templates_dir / "metadata.json"
        self.templates_db = self._load_templates_database()
        
    def _load_templates_database(self) -> Dict[str, Template]:
        """Load templates database from metadata file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    templates = {}
                    for name, template_data in data.items():
                        template_data['created_at'] = datetime.fromisoformat(template_data['created_at'])
                        template_data['updated_at'] = datetime.fromisoformat(template_data['updated_at'])
                        templates[name] = Template(**template_data)
                    return templates
            except Exception as e:
                console.print(f"[red]Error loading templates database: {e}[/red]")
        
        return {}
    
    def _save_templates_database(self) -> None:
        """Save templates database to metadata file."""
        try:
            data = {}
            for name, template in self.templates_db.items():
                template_dict = asdict(template)
                template_dict['created_at'] = template.created_at.isoformat()
                template_dict['updated_at'] = template.updated_at.isoformat()
                data[name] = template_dict
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving templates database: {e}[/red]")
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA256 checksum of template content."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def create_template(
        self,
        name: str,
        description: str,
        content: str,
        author: str,
        tags: List[str],
        technologies: List[str],
        is_official: bool = False
    ) -> Template:
        """Create a new template."""
        # Validate template name
        if not name or not name.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Template name must be alphanumeric with optional hyphens/underscores")
        
        # Check if template already exists
        if name in self.templates_db:
            raise ValueError(f"Template '{name}' already exists")
        
        # Create template object
        now = datetime.now()
        template = Template(
            name=name,
            description=description,
            content=content,
            author=author,
            version="1.0.0",
            tags=tags,
            technologies=technologies,
            created_at=now,
            updated_at=now,
            downloads=0,
            rating=0.0,
            is_official=is_official,
            is_custom=True,
            file_size=len(content.encode()),
            checksum=self._calculate_checksum(content)
        )
        
        # Save template file
        template_file = self.custom_dir / f"{name}.gitignore"
        template_file.write_text(content)
        
        # Add to database
        self.templates_db[name] = template
        self._save_templates_database()
        
        console.print(f"✅ Template '{name}' created successfully")
        return template
    
    async def update_template(
        self,
        name: str,
        description: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        technologies: Optional[List[str]] = None,
        version: Optional[str] = None
    ) -> Template:
        """Update an existing template."""
        if name not in self.templates_db:
            raise ValueError(f"Template '{name}' not found")
        
        template = self.templates_db[name]
        
        # Update fields
        if description is not None:
            template.description = description
        if content is not None:
            template.content = content
            template.file_size = len(content.encode())
            template.checksum = self._calculate_checksum(content)
            
            # Update file
            template_file = self.custom_dir / f"{name}.gitignore"
            template_file.write_text(content)
        
        if tags is not None:
            template.tags = tags
        if technologies is not None:
            template.technologies = technologies
        if version is not None:
            template.version = version
        
        template.updated_at = datetime.now()
        
        # Save to database
        self._save_templates_database()
        
        console.print(f"✅ Template '{name}' updated successfully")
        return template
    
    async def delete_template(self, name: str, force: bool = False) -> bool:
        """Delete a template."""
        if name not in self.templates_db:
            raise ValueError(f"Template '{name}' not found")
        
        template = self.templates_db[name]
        
        if not force and not Confirm.ask(f"Are you sure you want to delete template '{name}'?"):
            return False
        
        # Remove from database
        del self.templates_db[name]
        self._save_templates_database()
        
        # Remove file
        template_file = self.custom_dir / f"{name}.gitignore"
        if template_file.exists():
            template_file.unlink()
        
        console.print(f"✅ Template '{name}' deleted successfully")
        return True
    
    async def get_template(self, name: str) -> Optional[Template]:
        """Get a template by name."""
        return self.templates_db.get(name)
    
    async def list_templates(
        self,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        technologies: Optional[List[str]] = None,
        custom_only: bool = False,
        official_only: bool = False
    ) -> List[Template]:
        """List templates with optional filtering."""
        templates = list(self.templates_db.values())
        
        # Apply filters
        if search:
            search_lower = search.lower()
            templates = [
                t for t in templates
                if (search_lower in t.name.lower() or
                    search_lower in t.description.lower() or
                    any(search_lower in tag.lower() for tag in t.tags))
            ]
        
        if tags:
            templates = [
                t for t in templates
                if any(tag in t.tags for tag in tags)
            ]
        
        if technologies:
            templates = [
                t for t in templates
                if any(tech in t.technologies for tech in technologies)
            ]
        
        if custom_only:
            templates = [t for t in templates if t.is_custom]
        
        if official_only:
            templates = [t for t in templates if t.is_official]
        
        return sorted(templates, key=lambda t: t.downloads, reverse=True)
    
    def display_templates(self, templates: List[Template]) -> None:
        """Display templates in a beautiful table."""
        if not templates:
            console.print("No templates found")
            return
        
        table = Table(title="📚 Templates")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Author", style="green")
        table.add_column("Version", style="yellow")
        table.add_column("Downloads", style="blue")
        table.add_column("Rating", style="magenta")
        table.add_column("Type", style="bold")
        
        for template in templates:
            template_type = "Custom" if template.is_custom else "Official"
            table.add_row(
                template.name,
                template.description[:50] + "..." if len(template.description) > 50 else template.description,
                template.author,
                template.version,
                str(template.downloads),
                f"{template.rating:.1f}⭐" if template.rating > 0 else "N/A",
                template_type
            )
        
        console.print(table)
    
    async def export_template(self, name: str, output_path: Path) -> bool:
        """Export a template to a file."""
        template = await self.get_template(name)
        if not template:
            console.print(f"[red]Template '{name}' not found[/red]")
            return False
        
        try:
            # Create export data
            export_data = {
                "template": asdict(template),
                "exported_at": datetime.now().isoformat(),
                "exported_by": "gign"
            }
            
            # Convert datetime objects
            export_data["template"]["created_at"] = template.created_at.isoformat()
            export_data["template"]["updated_at"] = template.updated_at.isoformat()
            
            # Write to file
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            console.print(f"✅ Template '{name}' exported to {output_path}")
            return True
            
        except Exception as e:
            console.print(f"[red]Error exporting template: {e}[/red]")
            return False
    
    async def import_template(self, import_path: Path) -> bool:
        """Import a template from a file."""
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            template_data = import_data["template"]
            
            # Convert datetime strings back to datetime objects
            template_data["created_at"] = datetime.fromisoformat(template_data["created_at"])
            template_data["updated_at"] = datetime.fromisoformat(template_data["updated_at"])
            
            # Create template object
            template = Template(**template_data)
            
            # Check if template already exists
            if template.name in self.templates_db:
                if not Confirm.ask(f"Template '{template.name}' already exists. Overwrite?"):
                    return False
            
            # Save template
            template_file = self.custom_dir / f"{template.name}.gitignore"
            template_file.write_text(template.content)
            
            # Add to database
            self.templates_db[template.name] = template
            self._save_templates_database()
            
            console.print(f"✅ Template '{template.name}' imported successfully")
            return True
            
        except Exception as e:
            console.print(f"[red]Error importing template: {e}[/red]")
            return False
    
    async def share_template(self, name: str, share_url: str) -> bool:
        """Share a template to a remote repository."""
        template = await self.get_template(name)
        if not template:
            console.print(f"[red]Template '{name}' not found[/red]")
            return False
        
        try:
            # Create share package
            share_data = {
                "template": asdict(template),
                "share_url": share_url,
                "shared_at": datetime.now().isoformat()
            }
            
            # Convert datetime objects
            share_data["template"]["created_at"] = template.created_at.isoformat()
            share_data["template"]["updated_at"] = template.updated_at.isoformat()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(share_data, f, indent=2)
                temp_path = Path(f.name)
            
            console.print(f"✅ Template '{name}' prepared for sharing")
            console.print(f"Share file: {temp_path}")
            console.print(f"Share URL: {share_url}")
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error sharing template: {e}[/red]")
            return False


class TemplateMarketplace:
    """Template marketplace for discovering and downloading community templates."""
    
    def __init__(self):
        self.api_base = "https://api.github.com"
        self.marketplace_url = "https://raw.githubusercontent.com/gitignore-community/templates/main"
        self.cache_dir = Path.home() / ".gign" / "marketplace_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def discover_templates(
        self,
        category: Optional[str] = None,
        language: Optional[str] = None,
        trending: bool = False
    ) -> List[Dict]:
        """Discover templates from the marketplace."""
        try:
            # This would integrate with a real marketplace API
            # For now, return curated templates
            templates = [
                {
                    "name": "fullstack-web",
                    "description": "Complete web development stack with Node.js, React, and Python",
                    "author": "community",
                    "downloads": 1500,
                    "rating": 4.8,
                    "tags": ["web", "fullstack", "react", "node", "python"],
                    "technologies": ["node", "react", "python", "docker"]
                },
                {
                    "name": "microservices",
                    "description": "Microservices architecture with Docker, Kubernetes, and monitoring",
                    "author": "community",
                    "downloads": 1200,
                    "rating": 4.6,
                    "tags": ["microservices", "docker", "kubernetes", "monitoring"],
                    "technologies": ["docker", "kubernetes", "prometheus", "grafana"]
                },
                {
                    "name": "data-science",
                    "description": "Data science and machine learning with Python, Jupyter, and ML frameworks",
                    "author": "community",
                    "downloads": 2000,
                    "rating": 4.9,
                    "tags": ["data-science", "ml", "python", "jupyter"],
                    "technologies": ["python", "jupyter", "tensorflow", "pytorch"]
                }
            ]
            
            # Apply filters
            if category:
                templates = [t for t in templates if category in t["tags"]]
            
            if language:
                templates = [t for t in templates if language in t["technologies"]]
            
            if trending:
                templates = sorted(templates, key=lambda t: t["downloads"], reverse=True)
            
            return templates
            
        except Exception as e:
            console.print(f"[red]Error discovering templates: {e}[/red]")
            return []
    
    async def download_template(self, template_name: str) -> Optional[Template]:
        """Download a template from the marketplace."""
        try:
            # This would download from a real marketplace
            # For now, create a sample template
            template = Template(
                name=template_name,
                description=f"Downloaded template: {template_name}",
                content="# Downloaded template\n*.log\n*.tmp\n.env",
                author="marketplace",
                version="1.0.0",
                tags=["downloaded"],
                technologies=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                downloads=1,
                rating=0.0,
                is_official=False,
                is_custom=False,
                file_size=50,
                checksum=""
            )
            
            console.print(f"✅ Template '{template_name}' downloaded successfully")
            return template
            
        except Exception as e:
            console.print(f"[red]Error downloading template: {e}[/red]")
            return None
    
    def display_marketplace(self, templates: List[Dict]) -> None:
        """Display marketplace templates."""
        if not templates:
            console.print("No templates found in marketplace")
            return
        
        table = Table(title="🛒 Template Marketplace")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Author", style="green")
        table.add_column("Downloads", style="blue")
        table.add_column("Rating", style="magenta")
        table.add_column("Tags", style="yellow")
        
        for template in templates:
            tags_str = ", ".join(template["tags"][:3])
            table.add_row(
                template["name"],
                template["description"][:50] + "..." if len(template["description"]) > 50 else template["description"],
                template["author"],
                str(template["downloads"]),
                f"{template['rating']}⭐",
                tags_str
            )
        
        console.print(table)


class TemplateValidator:
    """Validate template content and structure."""
    
    @staticmethod
    def validate_template_content(content: str) -> Tuple[bool, List[str]]:
        """Validate template content."""
        errors = []
        
        if not content.strip():
            errors.append("Template content cannot be empty")
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                # Check for invalid patterns
                if line.startswith('/') and not line.endswith('/'):
                    errors.append(f"Line {i}: Invalid pattern '{line}' - absolute paths should end with '/'")
                
                if '**' in line and not line.endswith('/'):
                    errors.append(f"Line {i}: Invalid pattern '{line}' - '**' should be followed by '/'")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_template_name(name: str) -> Tuple[bool, List[str]]:
        """Validate template name."""
        errors = []
        
        if not name:
            errors.append("Template name cannot be empty")
        
        if len(name) > 50:
            errors.append("Template name too long (max 50 characters)")
        
        if not name.replace('-', '').replace('_', '').isalnum():
            errors.append("Template name must be alphanumeric with optional hyphens/underscores")
        
        return len(errors) == 0, errors


# Global instances
template_manager = TemplateManager()
template_marketplace = TemplateMarketplace()
template_validator = TemplateValidator() 