import os

# python-RQ and workers settings
RQ_QUEUE = os.getenv("RQ_QUEUE_NAME", "lab1")
RQ_QUEUES = {
    "lab1": "lab1",
    "lab2": "lab2",
}
RQ_JOBS_TIMEOUT = os.getenv("RQ_JOBS_DEFAULT_TIMEOUT", "10h")
IMAGE_FETCH_TIMEOUT = os.getenv("IMAGE_FETCH_TIMEOUT", 120)

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

LAB_PORT = os.getenv("LAB_PORT", 8080)
BACKEND_PORT = os.getenv("BACKEND_PORT", 8000)
# Lab Settings
TFTP_ROOT = os.getenv("TFTP_ROOT", "/opt/tftpboot/data")
TEMPLATE_DIR = os.getenv("TEMPLATE_DIR", "./templates")
