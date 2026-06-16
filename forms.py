"""WTForms definitions for authentication (CSRF token included automatically)."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    name = StringField(
        "Nom",
        validators=[DataRequired(message="Le nom est requis."),
                    Length(min=2, max=120, message="Le nom doit faire 2 à 120 caractères.")],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(message="L'email est requis."),
                    Email(message="Adresse email invalide."),
                    Length(max=255)],
    )
    password = PasswordField(
        "Mot de passe",
        validators=[DataRequired(message="Le mot de passe est requis."),
                    Length(min=8, max=128, message="Le mot de passe doit faire au moins 8 caractères.")],
    )
    confirm = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(message="Veuillez confirmer le mot de passe."),
                    EqualTo("password", message="Les mots de passe ne correspondent pas.")],
    )
    submit = SubmitField("Créer mon compte")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(message="L'email est requis."),
                    Email(message="Adresse email invalide."),
                    Length(max=255)],
    )
    password = PasswordField(
        "Mot de passe",
        validators=[DataRequired(message="Le mot de passe est requis.")],
    )
    submit = SubmitField("Se connecter")
