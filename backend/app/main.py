from app import config

if config.ROLE == "worker":
    from app.worker import app
else:
    from app.api import app

__all__ = ["app"]
