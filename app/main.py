import subprocess
import os
import sys

def run_streamlit_app():
    """
    Finds the project root and runs the Streamlit UI script from there.
    This ensures all module paths work correctly.
    """
    try:
        # The directory of this script (app/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # The project root directory (one level up from app/)
        project_root = os.path.dirname(script_dir)

        # The path to the Streamlit UI file, relative to the project root
        ui_script_path = os.path.join("app", "ui", "main_ui.py")

        print("="*50)
        print(f"  Project Root: {project_root}")
        print(f"  Launching UI: {ui_script_path}")
        print("="*50)

        # We use subprocess.run to execute the streamlit command.
        # We also set the 'cwd' (current working directory) to the project root.
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", ui_script_path],
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

if __name__ == "__main__":
    run_streamlit_app()