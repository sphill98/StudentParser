import subprocess
import sys
import os
import atexit
import signal
from config.config import Config

# --- Configuration ---
services = {
    "parsing_service": {
        "host": Config.PARSING_HOST,
        "port": Config.PARSING_PORT,
        "env": {}
    },
    "frontend_service": {
        "host": Config.FRONTEND_HOST,
        "port": Config.FRONTEND_PORT,
        "env": {"PARSING_SERVICE_URL": f"http://{Config.PARSING_HOST}:{Config.PARSING_PORT}", "FLASK_SECRET_KEY": Config.SECRET_KEY}
    },
    "auth_service": {
        "host": Config.AUTH_HOST,
        "port": Config.AUTH_PORT,
        "env": {}
    }
}

processes = []

def cleanup():
    print("\nStopping all services...")
    for p in processes:
        # Terminate the entire process group
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    print("All services stopped.")

# Register cleanup function to be called on script exit
atexit.register(cleanup)
signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))
signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))


def run_service(name, config):
    print(f"--- Starting {name} ---")
    service_dir = os.path.abspath(name)
    venv_dir = os.path.join(service_dir, ".venv")
    
    # 1. Create virtual environment (or recreate if it exists)
    if os.path.isdir(venv_dir):
        print(f"Removing existing virtual environment for {name}...")
        subprocess.run(["rm", "-rf", venv_dir], check=True)

    print(f"Creating virtual environment for {name}...")
    subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True, cwd=service_dir)

    # Determine python and pip executables
    python_executable = os.path.join(venv_dir, "bin", "python")
    pip_executable = os.path.join(venv_dir, "bin", "pip")

    # 2. Install dependencies
    print(f"Installing dependencies for {name}...")
    subprocess.run([pip_executable, "install", "-r", "requirements.txt"], check=True, cwd=service_dir)

    # 3. Start the Flask app
    print(f"Starting {name} on {config['host']}:{config['port']}...")
    
    # Prepare environment variables
    run_env = os.environ.copy()
    run_env.update({
        "FLASK_APP": "app.py"
    })
    run_env.update(config.get("env", {}))

    # Use os.setsid to create a new process session, making this process the group leader.
    # This allows us to kill the process and all its children (like the reloader) at once.
    app_module = f"{name}.app:app"
    process = subprocess.Popen(
        [os.path.join(venv_dir, "bin", "gunicorn"),
         "--workers", "1", # For development, 1 worker is usually enough
         "--bind", f"{config['host']}:{config['port']}",
         app_module],
        cwd=os.path.abspath(os.path.join(service_dir, os.pardir)),
        env=run_env,
        preexec_fn=os.setsid
    )
    processes.append(process)
    print(f"{name} started with PID: {process.pid}")
    return process

if __name__ == "__main__":
    # Start all services
    for name, config in services.items():
        run_service(name, config)

    print("\n" + "="*40)
    print("All services are running.")
    print("- FrontEnd Service (Frontend): http://" + Config.FRONTEND_HOST + ":" + str(Config.FRONTEND_PORT))
    print("- Parsing Service (API):     http://" + Config.PARSING_HOST + ":" + str(Config.PARSING_PORT))
    print("- Auth Service (Auth):       http://" + Config.AUTH_HOST + ":" + str(Config.AUTH_PORT))
    print("\nPress Ctrl+C to stop all services.")
    print("="*40 + "\n")

    # Wait for user to interrupt
    try:
        # Wait for all processes to complete. They won't, until killed.
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        sys.exit(0)