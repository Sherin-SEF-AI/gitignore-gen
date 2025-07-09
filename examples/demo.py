#!/usr/bin/env python3
"""Demo script showing how to use gign programmatically."""

import asyncio
from pathlib import Path

from gitignore_gen.core import GitignoreGenerator
from gitignore_gen.detector import TechnologyDetector


async def main():
    """Demonstrate gign functionality."""
    print("🚀 gign Demo")
    print("=" * 50)
    
    # Create a sample project structure
    project_dir = Path("demo-project")
    project_dir.mkdir(exist_ok=True)
    
    # Create some sample files to detect
    (project_dir / "requirements.txt").write_text("requests==2.31.0\nflask==2.3.0")
    (project_dir / "main.py").write_text("print('Hello, World!')")
    (project_dir / "package.json").write_text('{"name": "demo-project", "dependencies": {"react": "^18.0.0"}}')
    (project_dir / ".vscode").mkdir(exist_ok=True)
    (project_dir / ".vscode" / "settings.json").write_text("{}")
    
    print(f"📁 Created demo project in: {project_dir}")
    
    # Detect technologies
    print("\n🔍 Detecting technologies...")
    detector = TechnologyDetector()
    technologies = await detector.detect(project_dir)
    
    print(f"Found technologies: {', '.join(technologies)}")
    
    # Generate .gitignore
    print("\n🚀 Generating .gitignore...")
    async with GitignoreGenerator() as generator:
        content = await generator.generate(
            technologies,
            security_patterns=True,
            monorepo=False
        )
        
        # Save the .gitignore
        gitignore_path = project_dir / ".gitignore"
        await generator.save_gitignore(gitignore_path, content, backup=True)
        
        print(f"✅ Generated .gitignore: {gitignore_path}")
        
        # Show preview
        print("\n📋 Generated .gitignore preview:")
        print("-" * 40)
        lines = content.split('\n')[:20]  # Show first 20 lines
        for line in lines:
            print(line)
        if len(content.split('\n')) > 20:
            print("...")
        
        # Check for files that should be ignored
        print("\n🔍 Checking for files that should be ignored...")
        ignored_files = await generator.check_git_status(project_dir)
        
        if ignored_files:
            print("Files that should be ignored but are tracked:")
            for file_path in ignored_files[:5]:  # Show first 5
                print(f"  - {file_path}")
            if len(ignored_files) > 5:
                print(f"  ... and {len(ignored_files) - 5} more")
        else:
            print("✅ No files found that should be ignored")
    
    print(f"\n🎉 Demo completed! Check out {project_dir}/.gitignore")


if __name__ == "__main__":
    asyncio.run(main()) 