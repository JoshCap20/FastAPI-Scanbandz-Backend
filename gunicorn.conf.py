"""Gunicorn configuration file. (Production)

Gunicorn is a Python WSGI HTTP Server for UNIX. It's a pre-fork worker model.

See: https://docs.gunicorn.org/en/stable/configure.html#configuration-file
"""

# Worker configuration
import multiprocessing

# Server socket
bind = "0.0.0.0:8080"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
loglevel = "debug"
accesslog = "-"
errorlog = "-"

# Server mechanics
preload_app = True
reload = False  # Set to True for development

# Security
limit_request_line = 4094
limit_request_fields = 50
limit_request_field_size = 8190

# def on_starting(server):
#     """Called just before the master process is initialized."""
#     print("[GUNICORN] Starting server..")

# def on_reload(server):
#     """Called to recycle workers during a reload via SIGHUP."""
#     print("[GUNICORN] Reloading server..")

# def when_ready(server):
#     """Called just after the server is started."""
#     print("[GUNICORN] Server is ready.")
