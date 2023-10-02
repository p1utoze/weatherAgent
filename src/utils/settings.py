import os
from pathlib import Path

PARENT_DIR = Path(__file__).parent
PROJECT_ROOT = PARENT_DIR.parent.parent

ENV_PATH = PROJECT_ROOT / '.env'
