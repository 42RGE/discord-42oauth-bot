from flask import Blueprint, render_template, request, session
from extensions import db, client
from models.users import User
from flask import current_app as app, redirect, url_for
from urllib.parse import urlencode
import requests
from zenora import APIClient
from utils import *
from config import TOKEN, GUILD_ID, REDIRECT_URI, DISCORD_ROLE_ID

bp = Blueprint('oauth', __name__, url_prefix='/oauth')

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route('/authorize/<provider>/<discord_id>')
def oauth2_authorize(provider, discord_id):
    logged_user = db.session.scalar(db.select(User).where(User.discord_id == discord_id))
    if logged_user is None or logged_user.login is not None:
        return redirect(url_for('home'))
    provider_data = app.config['OAUTH2_PROVIDERS'][provider]
    params = {
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('oauth.callback_42', _external=True, discord_id=discord_id),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
    }
    return redirect(f'{provider_data["authorize_url"]}?{urlencode(params)}')

@bp.route('/callback')
def callback():
    code = request.args.get('code')
    access_token = client.oauth.get_access_token(code, REDIRECT_URI).access_token
    bearer_client = APIClient(access_token, bearer=True)
    session['token'] = access_token
    return redirect("/")

@bp.route('/callback/42')
def callback_42():
    provider_data = app.config['OAUTH2_PROVIDERS']['42']
    code = request.args.get('code')
    discord_id = request.args.get('discord_id')
    response = requests.post(provider_data['token_url'], data={
        'grant_type': 'authorization_code',
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': code,
        'redirect_uri': url_for('oauth.callback_42', _external=True, discord_id=discord_id),
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
    add_user_role(TOKEN, discord_id, GUILD_ID, DISCORD_ROLE_ID)
    db.session.commit()
    return redirect(url_for('home'))
