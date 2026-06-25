"""Authentication blueprint: register, login, logout."""
from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from forms import LoginForm, RegisterForm
from models import User

auth_bp = Blueprint("auth", __name__)


def _safe_next(target: str | None) -> str:
    """Only allow same-site relative redirects (avoid open-redirect)."""
    if not target:
        return url_for("home")
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not target.startswith("/") or target.startswith("//"):
        return url_for("home")
    return target


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if User.query.filter_by(email=email).first():
            flash("Un compte existe déjà avec cet email.", "error")
        else:
            user = User(name=form.name.data.strip(), email=email)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Compte créé avec succès. Bienvenue !", "success")
            return redirect(url_for("home"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Content de vous revoir, {user.name} !", "success")
            return redirect(_safe_next(request.args.get("next")))
        flash("Email ou mot de passe incorrect.", "error")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Vous êtes déconnecté.", "success")
    return redirect(url_for("auth.login"))
