from flask import Flask, render_template, request, session, redirect, url_for, flash
from zenora import APIClient
from config import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from urllib.parse import urlencode
import requests
from utils import change_user_nickname, add_user_to_server, remove_user_from_server, add_user_role

app = Flask(__name__)
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

client = APIClient(TOKEN, client_secret=CLIENT_SECRET)
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(64), nullable=False)
    login = db.Column(db.String(64), nullable=True)

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
                return redirect(url_for('oauth2_authorize', provider='42', discord_id=current_user_discord.id))
            return render_template('index.html', user=user)
        else:
            return render_template('index.html', user=user)

    return render_template('index.html', oauth_uri=OAUTH_URL)

@app.route('/oauth/callback')
def callback():
    code = request.args.get('code')
    access_token = client.oauth.get_access_token(code, REDIRECT_URI).access_token
    bearer_client = APIClient(access_token, bearer=True)
    session['token'] = access_token
    return redirect("/")

@app.route('/oauth/authorize/<provider>/<discord_id>')
def oauth2_authorize(provider, discord_id):
    logged_user = db.session.scalar(db.select(User).where(User.discord_id == discord_id))
    if logged_user is None or logged_user.login is not None:
        return redirect(url_for('home'))
    provider_data = app.config['OAUTH2_PROVIDERS'][provider]
    params = {
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('callback_42', _external=True, discord_id=discord_id),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
    }
    return redirect(f'{provider_data["authorize_url"]}?{urlencode(params)}')

@app.route('/callback/42')
def callback_42():
    provider_data = app.config['OAUTH2_PROVIDERS']['42']
    code = request.args.get('code')
    discord_id = request.args.get('discord_id')
    response = requests.post(provider_data['token_url'], data={
        'grant_type': 'authorization_code',
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': code,
        'redirect_uri': url_for('callback_42', _external=True, discord_id=discord_id),
    })
    access_token = response.json().get('access_token')
    response = requests.get(provider_data['userinfo']['url'],
    headers={
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
    })
    user = User.query.filter_by(discord_id=discord_id).first()
    content = response.json()
    user.login = content['login']
    first_name = content['usual_first_name'] if content['usual_first_name'] is not None \
    else content['first_name']
    add_user_to_server(TOKEN, discord_id, GUILD_ID, session['token'])
    change_user_nickname(TOKEN, discord_id, GUILD_ID, user.login, first_name)
    add_user_role(TOKEN, discord_id, GUILD_ID, 1246021012328419460)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


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
