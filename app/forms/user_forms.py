import re
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from app.models.user import User
from extensions import db

# ------ Helpers ----------------

def strong_password(form, field):
    """Require: min 8 char, upper, lower, digit, special."""
    password = field.data or ""
    if len(password) < 8:
        raise ValidationError ("PPassword must be at least 8 characters long.")

    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    
    if not re.search(r"[a-z]", password):
        raise ValidationError ("Password must contain at least one lowercase letter.")
    
    if not re.search(r"[0-9]", password):
        raise ValidationError("Password must contain at least one digit.")
    
    if not re.search(r"[!@#$%^&*(),.?/<>_\-+=]", password):
        raise ValidationError("Pasword must contain at least one special character.")

# -----------Create form passowrd required ------------

class UserCreateForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=120)],
        render_kw={"placeholder": "Enter username"},
    )
    
    email = StringField(
        "Email",
        validators = [DataRequired(), Email(), Length(max=120)],
        render_kw={"placeholder": "sample@gmail.com"}
    )
    
    full_name = StringField(
        "Full name",
        validators=[DataRequired(), Length(min=3, max=120)],
        render_kw={"placeholder": "Enter your full name"}
    )
    
    is_active = BooleanField("Active", default=True)

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            strong_password,
        ],
        render_kw={"placeholder": "Strong password"},
    )
    
    confirm_password = StringField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Password must match."),
        ],
        render_kw={"placeholder": "Confirm password"},
    )
    
    submit = SubmitField("Save")
    
# ------ server-side uniquess checks ---------------

    def validate_username(self, field):
        exists = db.session.scalar(
            db.select(User).filter(User.username == field.data)
        )
        if exists:
            raise ValidationError("This username is already is taken.")

    
    def validate_email(self, field):
        exists = db.session.scalar(
            db.select(User).filter(User.email == field.data)
        )
        if exists:
            raise ValidationError("This email is already registered.")


# ------- edit form (password optional) -----------

class UserEditForm(FlaskForm):
    username = StringField(
        "Username",
        validators = [DataRequired(), Length(min=3, max=120)],
    )
    
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    
    full_name = StringField(
        "Full name",
        validators=[DataRequired(), Length(min=3, max=120)],
    )
    
    is_active = BooleanField("Active")
    
    # optional password - only change if filled
    password = PasswordField(
        "New Password (leave blank to keek current)",
        validators=[strong_password],
        render_kw={"placeholder": "New strong password (optional)"},
    )  
    
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[EqualTo("password", message="Password must matche.")],
    )
    
    submit = SubmitField("Update")

    def __init__(self, original_user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_user = original_user
        
    def validate_username(self, field):
        q = db.select(User).filter(User.username == field.data, User.id != self.original_user.id)
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This username already taken.")

    def validate_email(self, field):
        q = db.select(User).filter(User.email == field.data, User.id != self.original_user.id)
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This email already registered.")

class ConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")
