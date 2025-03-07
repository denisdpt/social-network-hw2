import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import sys
import os.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
