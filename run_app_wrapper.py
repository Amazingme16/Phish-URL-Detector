import subprocess
import sys

log_path = r'c:\Users\hp\.gemini\app.log'

try:
    with open(log_path, 'w') as f:
        f.write("Starting app.py...\n")
        f.flush()
        # Use sys.executable to ensure we use the same python
        subprocess.call([sys.executable, 'app.py'], stdout=f, stderr=f)
        f.write("\nApp finished.\n")
except Exception as e:
    # Try one last ditch print to stderr (which might not be seen)
    print(f"Wrapper failed: {e}")
