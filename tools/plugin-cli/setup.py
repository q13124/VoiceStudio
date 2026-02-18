"""
Setup configuration for VoiceStudio Plugin CLI.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="voicestudio-plugin-cli",
    version="1.0.0",
    description="Command-line tool for VoiceStudio plugin development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="VoiceStudio Team",
    author_email="plugins@voicestudio.ai",
    url="https://github.com/voicestudio/voicestudio",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
    ],
    extras_require={
        "signing": [
            "cryptography>=41.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "voicestudio-plugin=cli:main",
            "vsp=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    keywords="voicestudio plugin cli development audio speech",
)
