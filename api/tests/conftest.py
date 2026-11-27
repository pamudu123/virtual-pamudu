import sys
from pathlib import Path

# Make `agent` and `main` importable when pytest runs from api/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
