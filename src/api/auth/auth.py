from flask import Blueprint, redirect, url_for, render_template, session, flash
from authlib.integrations.flask_client import OAuth
from functools import wraps
import json
import os
from src.api.models.paystack import is_user_pro

auth_bp = Blueprint('auth', __name__)
oauth = OAuth()


def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        "myApp",
        client_id=os.getenv("OAUTH2_CLIENT_ID"),    
        client_secret=os.getenv("OAUTH2_CLIENT_SECRET"), 
        server_metadata_url=os.getenv("OAUTH2_METADATA_URL"),
        client_kwargs={
            "scope": "openid email profile"
        }
    )

def pro_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user:
            flash('Please log in to access this feature')
            return redirect(url_for('auth.login'))
        
        email = user.get('email')
        pro_status = session.get('user_pro_status', False)
        
        if not email or (not is_user_pro(email) and not pro_status):
            flash('This feature requires a pro subscription')
            return redirect(url_for('auth.login'))
        
        print(f"Pro access granted for {email}")  # Debug log
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/signup")
def signup():
    '''signup page'''
    return render_template("signup.html")


@auth_bp.route("/googleLogin")
def googleLogin():
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("auth.googleCallback", _external=True))        


@auth_bp.route("/signin-google")
def googleCallback():
    '''redirect after pro'''
    token = oauth.myApp.authorize_access_token()
    session["user"] = token
    return redirect(url_for("auth.home"))

@auth_bp.route('/login')
def login():
    user = session.get("user")
    pro = False
    if user and user.get("email"):
        email = user.get("email")
        pro = is_user_pro(email) or session.get('user_pro_status', False)
        print(f"Login pro status for {email}: {pro}")  # Debug log
    return render_template("login.html", pro=pro, user=user)

