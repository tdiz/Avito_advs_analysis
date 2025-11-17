#!/usr/bin/env python3
"""
Обертка для запуска main.py с правильным PYTHONPATH

Использование:
    python run.py --query "ноутбук" --location "moskva" --pages 2
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Импортируем и запускаем main
from main import main

if __name__ == "__main__":
    main()
