"""
Установочный скрипт для Avito Ads Analysis Bot
"""
from setuptools import setup, find_packages
from pathlib import Path

# Читаем README для long_description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Читаем requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="avito-ads-analysis",
    version="1.0.0",
    author="Your Name",
    description="Бот для парсинга и анализа объявлений с Avito",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/avito-ads-analysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "avito-bot=main:main",
        ],
    },
)
