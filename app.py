from flask import Flask, render_template, request, session, redirect, url_for, flash
from zenora import APIClient
from config import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from urllib.parse import urlencode
import requests

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

def check_variables_exist():
    variables = {
            'DISCORD_TOKEN': TOKEN,
            'CLIENT_SECRET': CLIENT_SECRET,
            'DISCORD_REDIRECT_URI': REDIRECT_URI,
            'DISCORD_OAUTH_URL': OAUTH_URL,
            'DISCORD_GUILD_ID': GUILD_ID,
            '42_CLIENT_ID': FTWO_CLIENT_ID,
            '42_CLIENT_SECRET': FTWO_CLIENT_SECRET
        }

    missing_vars = [var_name for var_name, var_value in variables.items() if var_value is None]
    if missing_vars:
        raise ValueError(f'Missing environment variables: {", ".join(missing_vars)}')



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
    db.session.commit()
    return redirect(url_for('home'))

def change_user_nickname(token: str, user_id: str, server_id: str, nickname: str, usual_first_name: str) -> bool:

    url = f'https://discordapp.com/api/v8/guilds/{server_id}/members/{user_id}'
    headers = {
        'Authorization': f'Bot {token}'
    }
    data = {
        "nick": f'{nickname} ({usual_first_name})'
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200 or response.status_code == 204:
        return True
    print(f'Error changing nickname for user {user_id} in server with ID {server_id}')
    return False


def add_user_to_server(token: str, user_id: str, server_id: str, access_token: str) -> bool:
    url = f'https://discordapp.com/api/v8/guilds/{server_id}/members/{user_id}'
    headers = {
        'Authorization': f'Bot {token}'
    }

    data = {
        "access_token": access_token
    }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f'User {user_id} added to server with ID {server_id}')
        return True
    else:
        print(f'Error adding user {user_id} to server with ID {server_id}')
        return False

@app.route('/logout')
def logout():
    session.clear()
    db.delete(User)
    return redirect("/")

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    check_variables_exist()
    app.run(debug=True, port=4242)
