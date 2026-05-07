import sys
from pathlib import Path

# Add tools/req to sys.path so `import req` works in tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
