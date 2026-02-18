"""
VoiceStudio Plugin SDK setup configuration.
"""

import os

from setuptools import find_packages, setup

# Read version from package
here = os.path.abspath(os.path.dirname(__file__))
version = "1.0.0"

# Try to read from __init__.py
init_path = os.path.join(here, "voicestudio_sdk", "__init__.py")
if os.path.exists(init_path):
    with open(init_path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip("'\"")
                break

# Read README if available
readme_path = os.path.join(here, "README.md")
long_description = "VoiceStudio Plugin SDK"
if os.path.exists(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="voicestudio-plugin-sdk",
    version=version,
    description="SDK for developing VoiceStudio plugins",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="VoiceStudio Team",
    author_email="dev@voicestudio.app",
    url="https://github.com/voicestudio/voicestudio-plugin-sdk",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.9",
    install_requires=[
        # No hard dependencies - keep the SDK lightweight
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ],
        "async": [
            "aiofiles>=23.0.0",
        ],
        "audio": [
            "numpy>=1.20.0",
            "soundfile>=0.12.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Typing :: Typed",
    ],
    keywords=[
        "voicestudio",
        "plugin",
        "sdk",
        "audio",
        "speech",
        "synthesis",
        "transcription",
        "tts",
        "stt",
    ],
    package_data={
        "voicestudio_sdk": [
            "py.typed",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
