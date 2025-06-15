import sys
print(f"Python executable: {sys.executable}")
print(f"Python sys.path: {sys.path}")
try:
    import dateutil
    print(f"Successfully imported dateutil. Version: {dateutil.__version__}")
except ImportError as e:
    print(f"Failed to import dateutil directly: {e}")
except Exception as e:
    print(f"An unexpected error occurred while importing dateutil: {e}")
