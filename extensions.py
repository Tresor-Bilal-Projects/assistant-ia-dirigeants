"""Shared Flask extension singletons.

Kept in a dedicated module so models, blueprints and the app factory can all
import the same instances without creating circular imports.
"""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
