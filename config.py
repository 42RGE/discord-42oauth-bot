import os
import dotenv

dotenv.load_dotenv()

TOKEN=os.environ.get('DISCORD_TOKEN')
CLIENT_SECRET=os.environ.get('DISCORD_CLIENT_SECRET')
REDIRECT_URI=os.environ.get('DISCORD_REDIRECT_URI')
OAUTH_URL=os.environ.get('DISCORD_OAUTH_URL')
GUILD_ID=os.environ.get('DISCORD_GUILD_ID')
FTWO_CLIENT_ID=os.environ.get('42_CLIENT_ID')
FTWO_CLIENT_SECRET=os.environ.get('42_CLIENT_SECRET')
