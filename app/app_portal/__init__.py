from flask import Blueprint

app_portal_bp = Blueprint(
    "app_portal",
    __name__,
    template_folder="templates"
)

from app.app_portal import routes