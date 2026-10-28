"""Test fixture assessment that raises at import time (the loader must report it)."""

raise RuntimeError("this assessment module cannot load")
