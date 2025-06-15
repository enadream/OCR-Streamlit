import os
import sys
from pathlib import Path
import subprocess

# Add the project root to the Python path to ensure all imports work correctly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def setup_directories():
    """
    Ensures that the main 'app/data' directory exists before the app starts.
    Other modules are expected to create their own subdirectories as needed.
    """
    print("[INFO]: Setting up data directory...")
    # Define the path to the main data directory, relative to this script's location.
    app_dir = Path(__file__).parent
    data_dir = app_dir / "data"
    
    # Create the data directory. 'exist_ok=True' prevents an error if it already exists.
    data_dir.mkdir(exist_ok=True)
    print(f"  -> Ensuring '{data_dir}' exists.")
    print("[INFO]: Directory setup complete.")

def run_streamlit_app():
    """
    Finds the project root and runs the Streamlit UI script from there.
    This ensures all module paths and file access work correctly.
    """
    try:
        # The project root is one level up from this script's directory (app/).
        project_root = Path(__file__).resolve().parent.parent
        ui_script_path = project_root / "app" / "ui" / "main_ui.py"

        print("="*50)
        print(f"  Project Root: {project_root}")
        print(f"  Launching UI: {ui_script_path}")
        print("="*50)

        # Use subprocess to run streamlit, setting the current working directory
        # to the project root. This is a robust way to launch the app.
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(ui_script_path)],
            check=True,
            cwd=project_root 
        )

    except FileNotFoundError:
        print("\n[ERROR] Could not run Streamlit.")
        print("Please ensure Streamlit is installed in your virtual environment.")
        print("Try running: pip install streamlit")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] The Streamlit app exited with an error: {e}")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == '__main__':
    # 1. Set up the file system structure first.
    setup_directories()
    
    # 2. Launch the Streamlit UI.
    run_streamlit_app()