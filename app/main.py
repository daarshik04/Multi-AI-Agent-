import subprocess
import sys
import threading
import time
from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)
load_dotenv()


def run_backend():
    try:
        logger.info("Starting backend service..")
        subprocess.run(
            ["uvicorn", "app.backend.api:app", "--host", "127.0.0.1", "--port", "9999"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        # FIX (main.py): was catching CustomException but subprocess.run raises
        # subprocess.CalledProcessError — CustomException was never triggered,
        # so backend crashes were silently swallowed.
        logger.error(f"Backend process failed: {e}")
        raise


def run_frontend():
    try:
        logger.info("Starting Frontend service")
        subprocess.run(["streamlit", "run", "app/frontend/ui.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Frontend process failed: {e}")
        raise


if __name__ == "__main__":
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    # Give uvicorn time to start before launching Streamlit
    time.sleep(2)

    run_frontend()