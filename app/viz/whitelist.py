"""
Module allowlist for secure visualization sandbox.

This module defines the strict allowlist of imports permitted within
the visualization sandbox to prevent malicious code execution and
ensure security isolation.
"""

import sys
from typing import Set, Dict, Any
import importlib
import logging

logger = logging.getLogger(__name__)

# Allowed modules and their permitted attributes
ALLOWED_IMPORTS: Dict[str, Set[str]] = {
    # Core matplotlib modules
    "matplotlib": {
        "pyplot", "figure", "axes", "patches", "colors", "cm", "colorbar",
        "ticker", "dates", "font_manager", "rcParams", "use", "get_backend"
    },
    "matplotlib.pyplot": {
        "figure", "subplot", "subplots", "plot", "scatter", "bar", "hist",
        "boxplot", "pie", "imshow", "contour", "contourf", "xlabel", "ylabel",
        "title", "legend", "grid", "xlim", "ylim", "xticks", "yticks",
        "tight_layout", "savefig", "close", "clf", "cla", "gcf", "gca"
    },
    "matplotlib.figure": {"Figure"},
    "matplotlib.axes": {"Axes"},
    
    # Seaborn for statistical plots
    "seaborn": {
        "barplot", "boxplot", "violinplot", "scatterplot", "lineplot",
        "histplot", "kdeplot", "heatmap", "pairplot", "distplot",
        "countplot", "regplot", "lmplot", "set_style", "set_palette",
        "color_palette", "despine"
    },
    
    # NumPy for numerical operations
    "numpy": {
        "array", "arange", "linspace", "zeros", "ones", "full", "random",
        "mean", "median", "std", "var", "min", "max", "sum", "sort",
        "argsort", "argmin", "argmax", "where", "unique", "concatenate",
        "reshape", "transpose", "dot", "matmul", "pi", "e", "inf", "nan",
        "isnan", "isinf", "isfinite"
    },
    
    # Pandas for data manipulation (subset only)
    "pandas": {
        "DataFrame", "Series", "Index", "read_csv", "read_json",
        "to_datetime", "concat", "merge", "groupby", "pivot_table",
        "cut", "qcut", "get_dummies", "melt", "crosstab"
    },
    
    # Built-in modules for data processing
    "io": {"BytesIO", "StringIO"},
    "base64": {"b64encode", "b64decode"},
    "json": {"dumps", "loads"},
    "datetime": {"datetime", "date", "time", "timedelta"},
    "math": {
        "ceil", "floor", "round", "sqrt", "pow", "log", "log10", "exp",
        "sin", "cos", "tan", "pi", "e"
    },
    "statistics": {"mean", "median", "mode", "stdev", "variance"},
}

# Completely banned modules that should never be accessible
BANNED_IMPORTS: Set[str] = {
    # Filesystem access
    "os", "sys", "pathlib", "glob", "shutil", "tempfile", "zipfile",
    "tarfile", "gzip", "bz2",
    
    # Network access
    "urllib", "urllib.request", "urllib.parse", "requests", "http",
    "socket", "ssl", "ftplib", "smtplib", "poplib", "imaplib",
    
    # Process control
    "subprocess", "multiprocessing", "threading", "concurrent",
    "asyncio", "signal",
    
    # System introspection
    "inspect", "gc", "ctypes", "marshal", "pickle", "shelve",
    
    # Code execution
    "eval", "exec", "compile", "code", "ast",
    
    # Import system manipulation
    "importlib", "imp", "__import__"
}

class RestrictedImporter:
    """Custom import hook that restricts module imports to allowlist."""
    
    def __init__(self):
        self.original_import = __builtins__.__import__
        
    def __call__(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Restricted import function that only allows whitelisted modules."""
        
        # Check if module is banned
        if name in BANNED_IMPORTS or any(name.startswith(banned + ".") for banned in BANNED_IMPORTS):
            raise ImportError(f"Import of '{name}' is not allowed in sandbox")
        
        # Check if module is in allowlist
        if name not in ALLOWED_IMPORTS and not any(name.startswith(allowed + ".") for allowed in ALLOWED_IMPORTS):
            raise ImportError(f"Import of '{name}' is not allowed in sandbox")
        
        # Log allowed import
        logger.debug(f"Allowing import of '{name}' in sandbox")
        
        # Use original import
        return self.original_import(name, globals, locals, fromlist, level)

def install_import_restrictions():
    """Install the restricted import hook."""
    __builtins__.__import__ = RestrictedImporter()
    logger.info("Import restrictions installed")

def remove_import_restrictions():
    """Remove the restricted import hook (for cleanup)."""
    if hasattr(RestrictedImporter, 'original_import'):
        __builtins__.__import__ = RestrictedImporter().original_import
        logger.info("Import restrictions removed")

def validate_safe_environment():
    """Validate that the current environment is safe for sandbox execution."""
    dangerous_builtins = ['eval', 'exec', 'compile', 'open', '__import__']
    
    for builtin_name in dangerous_builtins:
        if builtin_name in dir(__builtins__) and builtin_name != '__import__':
            logger.warning(f"Dangerous builtin '{builtin_name}' is available")
    
    # Check for dangerous modules already imported
    dangerous_modules = BANNED_IMPORTS.intersection(set(sys.modules.keys()))
    if dangerous_modules:
        logger.warning(f"Dangerous modules already imported: {dangerous_modules}")
    
    return True

# Security configuration constants
MAX_CPU_TIME = 10  # seconds
MAX_MEMORY = 512 * 1024 * 1024  # 512MB
MAX_IMAGE_SIZE = (2048, 2048)  # pixels
MAX_DATA_ROWS = 5000  # Maximum rows to process
