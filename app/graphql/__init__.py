from flask import Blueprint

graphql = Blueprint('graphql', __name__)

from . import views
