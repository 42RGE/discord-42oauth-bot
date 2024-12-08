from flask import Flask, render_template, request, session, redirect, url_for, flash
from zenora import APIClient
from config import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from urllib.parse import urlencode
import requests
from utils import change_user_nickname, add_user_to_server, remove_user_from_server, add_user_role
from extensions import db, client
from models.users import User
from blueprint.oauth import bp as oauth_bp


app = Flask(__name__)
app.register_blueprint(oauth_bp)
app.config['SECRET_KEY'] = 'top secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH2_PROVIDERS'] = {
    '42': {
        'client_id': FTWO_CLIENT_ID,
        'client_secret': FTWO_CLIENT_SECRET,
        'authorize_url': 'https://api.intra.42.fr/oauth/authorize',
        'token_url': 'https://api.intra.42.fr/oauth/token',
        'userinfo': {
            'url': 'https://api.intra.42.fr/v2/me',
        },
        'scopes': ['public'],
    }
}

db.init_app(app)

login = LoginManager(app)
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

@app.route('/')
def home():
    if 'token' in session:
        bearer_client = APIClient(session['token'], bearer=True)
        current_user_discord = bearer_client.users.get_current_user()
        user = db.session.scalar(db.select(User).where(User.discord_id == current_user_discord.id))
        if user is None:
            user = User(discord_id=current_user_discord.id)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            if user.login is None:
                return redirect(url_for('oauth.oauth2_authorize', provider='42', discord_id=current_user_discord.id))
            return render_template('index.html', user=user)
        else:
            return render_template('index.html', user=user)

    return render_template('index.html', oauth_uri=OAUTH_URL)





@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


@app.route('/health')
def health():
    return "OK"

@app.route('/delete_account')
def delete_account():
    if 'token' in session:
        bearer_client = APIClient(session['token'], bearer=True)
        current_user_discord = bearer_client.users.get_current_user()
        user = db.session.scalar(db.select(User).where(User.discord_id == current_user_discord.id))
        if user is not None:
            remove_user_from_server(TOKEN, user.discord_id, GUILD_ID)
            db.session.delete(user)
            db.session.commit()
            session.clear()
    return redirect("/")


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    check_variables_exist()
    app.run(debug=True, port=4242)
