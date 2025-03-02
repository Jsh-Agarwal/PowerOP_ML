bind = "0.0.0.0:8000"
workers = 4
timeout = 600
loglevel = "debug"
capture_output = True
enable_stdio_inheritance = True
preload_app = True
worker_class = "uvicorn.workers.UvicornWorker"
