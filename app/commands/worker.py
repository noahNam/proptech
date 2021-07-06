from flask import current_app


@current_app.cli.command("start-worker")
def start_worker():
    print("*" * 30)
    print("*" * 30)
    print("*" * 30)
