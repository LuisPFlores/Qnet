"""
run_server.py – Production entry point for IIS HttpPlatformHandler.

IIS will launch this script and proxy HTTP traffic to Waitress on the
port provided via the %HTTP_PLATFORM_PORT% environment variable.

Do NOT use Flask's built-in dev server in production.
"""

import os
import sys
import logging

# Ensure the application root is on sys.path so imports work when IIS
# starts the process from an arbitrary working directory.
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from waitress import serve  # noqa: E402
from app import app          # noqa: E402

# ── Logging to file so you can debug IIS issues ──────────────────────
LOG_DIR = os.path.join(APP_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "qnet_iis.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("qnet.iis")

if __name__ == "__main__":
    # IIS HttpPlatformHandler injects the port it expects us to listen on.
    port = int(os.environ.get("HTTP_PLATFORM_PORT", "5000"))

    logger.info(f"Starting Waitress on 127.0.0.1:{port}")
    logger.info(f"Application directory: {APP_DIR}")

    serve(
        app,
        host="127.0.0.1",
        port=port,
        threads=4,
        channel_timeout=120,
        url_scheme="https",
    )
