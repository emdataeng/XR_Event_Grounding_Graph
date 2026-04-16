#!/usr/bin/env python3
"""check_env.py — Validate runtime dependencies before running the pipeline.

Run this once after setting up a new environment to confirm everything needed
is installed and optionally report GPU/HF availability.

Usage:
    python scripts/check_env.py
"""
import sys
import importlib
from pathlib import Path

# ── colour helpers (no dependencies) ────────────────────────────────────────
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def _ok(msg):  print(f"  {GREEN}✓{RESET} {msg}")
def _warn(msg): print(f"  {YELLOW}⚠{RESET}  {msg}")
def _fail(msg): print(f"  {RED}✗{RESET} {msg}")


def _check(pkg, import_name=None, required=True, version_attr="__version__"):
    name = import_name or pkg
    try:
        mod = importlib.import_module(name)
        ver = getattr(mod, version_attr, "?")
        _ok(f"{pkg}  ({ver})")
        return True
    except ImportError:
        if required:
            _fail(f"{pkg}  — MISSING (required)  →  pip install {pkg}")
        else:
            _warn(f"{pkg}  — not installed (optional)  →  pip install {pkg}")
        return False


def main():
    ok = True

    print(f"\n{BOLD}Python{RESET}")
    vi = sys.version_info
    if vi >= (3, 9):
        _ok(f"Python {vi.major}.{vi.minor}.{vi.micro}")
    else:
        _fail(f"Python {vi.major}.{vi.minor}.{vi.micro}  — need ≥ 3.9")
        ok = False

    print(f"\n{BOLD}Core pipeline dependencies{RESET}")
    for pkg, imp in [
        ("pandas", None), ("numpy", None), ("scipy", None),
        ("yaml", "yaml"), ("pydantic", None), ("networkx", None),
        ("PIL", "PIL"), ("matplotlib", None),
        ("rich", None), ("typer", None), ("dotenv", "dotenv"),
    ]:
        if not _check(pkg, imp):
            ok = False
    # cv2 install name differs from import name
    try:
        import cv2
        _ok(f"cv2  ({cv2.__version__})")
    except ImportError:
        _fail("cv2  — MISSING (required)  →  pip install opencv-python-headless")
        ok = False

    print(f"\n{BOLD}Open-vocabulary detection (required for grounding_dino / mm_grounding_dino backends){RESET}")
    torch_ok = _check("torch", required=False)
    _check("torchvision", required=False)
    _check("transformers", required=False)
    _check("accelerate", required=False)
    _check("safetensors", required=False)
    _check("huggingface_hub", required=False)

    if torch_ok:
        try:
            import torch
            if torch.cuda.is_available():
                _ok(f"CUDA available — {torch.cuda.get_device_name(0)}")
            else:
                _warn("CUDA not available — running on CPU (detection will be slow)")
        except Exception:
            pass

    print(f"\n{BOLD}YOLO (fixed-class detection backend){RESET}")
    _check("ultralytics", required=False)

    print(f"\n{BOLD}Graph export{RESET}")
    _check("neo4j", required=False)

    print(f"\n{BOLD}HuggingFace CLI{RESET}")
    import shutil
    if shutil.which("huggingface-cli"):
        _ok("huggingface-cli found")
    else:
        _warn("huggingface-cli not found  →  pip install huggingface_hub")

    print()
    if ok:
        print(f"{GREEN}{BOLD}Environment looks good.{RESET}")
    else:
        print(f"{RED}{BOLD}Some required packages are missing. Install them before running the pipeline.{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
