#!/usr/bin/env python3
"""Setup script for gign."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()



setup(
    name="gign",
    version="1.1.0",
    author="sherin joseph roy",
    author_email="sherin.joseph2217@gmail.com",
    maintainer="sherin joseph roy",
    maintainer_email="sherin.joseph2217@gmail.com",
    description="A magical CLI tool that automatically generates and manages .gitignore files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords=["git", "gitignore", "cli", "developer-tools", "automation"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "colorama>=0.4.6",
        "requests>=2.31.0",
        "gitpython>=3.1.0",
        "pyyaml>=6.0",
        "toml>=0.10.2",
        "aiohttp>=3.8.0",
        "aiofiles>=23.0.0",
        "pathspec>=0.11.0",
        "typing-extensions>=4.5.0",
        "watchdog>=3.0.0",
        "dataclasses-json>=0.6.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "twine>=4.0.0",
            "build>=0.10.0",
        ],
        "watch": ["watchdog>=3.0.0"],
    },
    entry_points={
        "console_scripts": [
            "gign=gitignore_gen.cli:main",
        ],
    },
    project_urls={
        "Homepage": "https://github.com/Sherin-SEF-AI/gitignore-gen",
        "Documentation": "https://github.com/Sherin-SEF-AI/gitignore-gen#readme",
        "Repository": "https://github.com/Sherin-SEF-AI/gitignore-gen",
        "Bug Tracker": "https://github.com/Sherin-SEF-AI/gitignore-gen/issues",
        "Changelog": "https://github.com/Sherin-SEF-AI/gitignore-gen/blob/main/CHANGELOG.md",
    },
    zip_safe=False,
) 