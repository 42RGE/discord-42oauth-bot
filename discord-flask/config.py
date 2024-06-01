import os
import dotenv

dotenv.load_dotenv()

TOKEN=os.environ.get('DISCORD_TOKEN')
CLIENT_SECRET=os.environ.get('DISCORD_CLIENT_SECRET')
REDIRECT_URI=os.environ.get('DISCORD_REDIRECT_URI')
OAUTH_URL=os.environ.get('DISCORD_OAUTH_URL')
GUILD_ID=os.environ.get('DISCORD_GUILD_ID')
FTWO_CLIENT_ID=os.environ.get('FT_CLIENT_ID')
FTWO_CLIENT_SECRET=os.environ.get('FT_CLIENT_SECRET')
DISCORD_ROLE_ID=int(os.environ.get('DISCORD_ROLE_ID', ""))


def check_variables_exist():
    variables = {
        'DISCORD_TOKEN': TOKEN,
        'CLIENT_SECRET': CLIENT_SECRET,
        'DISCORD_REDIRECT_URI': REDIRECT_URI,
        'DISCORD_OAUTH_URL': OAUTH_URL,
        'DISCORD_GUILD_ID': GUILD_ID,
        'FT_CLIENT_ID': FTWO_CLIENT_ID,
        'FT_CLIENT_SECRET': FTWO_CLIENT_SECRET,
        'DISCORD_ROLE_ID': DISCORD_ROLE_ID
    }

    missing_vars = [var_name for var_name, var_value in variables.items() if var_value is None]
    if missing_vars:
        raise ValueError(f'Missing environment variables: {", ".join(missing_vars)}')
