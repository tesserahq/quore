"""
Celery worker launcher.

This script is responsible for starting a Celery worker with
pool and concurrency settings driven by environment variables.
Important: Celery worker *processes* affect PostgreSQL connection
usage. Each OS process creates its own SQLAlchemy Engine and its
own connection pool, which means:

- prefork pool => concurrency N = N child processes
- each child process has its own DB connection pool
- total DB connections = (# processes) * (pool_size + max_overflow)

On macOS, `solo` is used by default to avoid fork-related issues,
resulting in a single OS process regardless of concurrency.

The final worker command is constructed dynamically and passed
to Celery via `worker_main()`.
"""

import os
import sys
import socket

from app.core.celery_app import celery_app


def main():
    loglevel = os.getenv("CELERY_LOGLEVEL", "info")
    # Determine Celery worker pool implementation.
    # - "prefork" (default on Linux): creates multiple OS processes equal to concurrency.
    # - "solo" (used on macOS): runs everything in a single process; safer for local dev.
    #   Important: Only OS processes affect DB connection count, NOT concurrency when using solo.
    default_pool = "solo" if sys.platform == "darwin" else "prefork"
    pool = os.getenv("CELERY_POOL", default_pool)
    # Concurrency determines the number of worker processes (for prefork)
    # or threads/greenlets (for other pool types).
    # For prefork:
    #   concurrency = N  =>  N OS processes => N SQLAlchemy connection pools.
    # For solo:
    #   concurrency has no impact on DB connections (only one process exists).
    concurrency = os.getenv("CELERY_CONCURRENCY", "1" if pool == "solo" else "4")
    queues = os.getenv("CELERY_QUEUES", "quore")  # Default to chrona queue

    # Generate a unique worker node name so that multiple workers can run without collisions.
    hostname = socket.gethostname()
    pid = os.getpid()
    nodename = os.getenv("CELERY_NODENAME", f"quore-worker@{hostname}-{pid}")

    # Build argument list passed to Celery. Celery interprets these exactly like CLI flags.
    argv = [
        "worker",
        f"--loglevel={loglevel}",
        f"--pool={pool}",
        f"--concurrency={concurrency}",
        f"--queues={queues}",  # Always specify queues
        f"--hostname={nodename}",  # Unique node name to avoid duplicate warnings
    ]
    celery_app.worker_main(argv)


if __name__ == "__main__":
    main()
