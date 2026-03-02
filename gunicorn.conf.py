# Gunicorn configuration file
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Request limits
max_requests = 1000
max_requests_jitter = 100

# File upload limits - IMPORTANT for large PDFs
limit_request_line = 8190
limit_request_fields = 200
limit_request_field_size = 16380

# CRITICAL: Set max request body size to 100MB for file uploads
max_body_size = 100 * 1024 * 1024  # 100MB

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "icolour-app"

# Worker restart
preload_app = True
reload = True

# Security
user = None
group = None
tmp_upload_dir = None

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def worker_int(worker):
    worker.log.info(f"Worker received INT or QUIT signal (pid: {worker.pid})")

def on_exit(server):
    server.log.info("Master shutting down")