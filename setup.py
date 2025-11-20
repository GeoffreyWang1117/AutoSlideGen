"""
Setup script for AutoSlideGen.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="autoslidegen",
    version="0.1.0",
    description="Automated PowerPoint outline generator using LLM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AutoSlideGen Team",
    author_email="",
    url="https://github.com/GeoffreyWang1117/AutoSlideGen",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "autoslidegen=autoslidegen.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="powerpoint ppt presentation llm ai automation",
    project_urls={
        "Bug Reports": "https://github.com/GeoffreyWang1117/AutoSlideGen/issues",
        "Source": "https://github.com/GeoffreyWang1117/AutoSlideGen",
    },
)
