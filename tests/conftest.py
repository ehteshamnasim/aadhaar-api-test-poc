"""
Pytest configuration for test suite
Adds parent directory to Python path for imports
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
