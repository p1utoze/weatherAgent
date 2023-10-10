import os
from pathlib import Path

# SET THE PROJECT PATH VARIABLES FOR THE PROJECT
PARENT_DIR = Path(__file__).parent # src/
PROJECT_ROOT = PARENT_DIR.parent.parent # /{projectName}/
ENV_PATH = PROJECT_ROOT / '.env'
