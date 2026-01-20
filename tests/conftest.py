import sys
import os
from pathlib import Path

# Add the project root to sys.path so we can import src
# This assumes conftest.py is in /tests/ and src is in /src/
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir / "src"))
