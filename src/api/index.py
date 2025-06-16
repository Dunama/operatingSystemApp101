import sys
import os

# Add the parent directory to Python path for Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from cs_205.app import app

# Export app for Vercel
if __name__ == "__main__":
    app.run()