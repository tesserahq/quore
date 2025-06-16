from app.core.celery_app import celery_app


def main():
    argv = [
        "worker",
        "--loglevel=info",
    ]
    celery_app.worker_main(argv)


if __name__ == "__main__":
    main()
