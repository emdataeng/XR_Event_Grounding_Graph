"""Root conftest — add XR_Pipeline to sys.path so 'import src.*' works
whether pytest is run as 'pytest' or 'python -m pytest'."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
