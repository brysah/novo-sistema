import os
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).parent
    NEWSLETTERS_FILE = BASE_DIR / 'newsletters.json'
    # Adicione outras configs conforme necessário

config = Config()
