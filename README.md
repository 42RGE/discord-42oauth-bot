
# <p align="center">Discord 42oauth bot</p>

This repo is a simple flask app that uses the 42 and Discord API in order to authenticate, rename and add a user to a discord server with a specific role.

I have tried to keep the code as simple as possible in order to make it easy to understand and modify for your own use case.

## Features
- Add a user to a guild based on their Discord ID and 42 login
- Rename the user to their 42 login
- Remove the user from the guild

### Quick Start

First of all, you need to create a new application on the [Discord Developer Portal](https://discord.com/developers/applications) and get the client ID and client secret.

Then, you need to create a new application on the [42 API](https://profile.intra.42.fr/oauth/applications) and get the UID and secret.

When they are created, you will need to create a `.env` file in the root of the project with the following content:

```env
FT_CLIENT_ID=
FT_CLIENT_SECRET=
DISCORD_TOKEN=
DISCORD_CLIENT_SECRET=
DISCORD_REDIRECT_URI=
DISCORD_OAUTH_URL=
DISCORD_GUILD_ID=
DISCORD_ROLE_ID=
```

> **Note:** The `DISCORD_REDIRECT_URI` should be the same as the one you set on the Discord Developer Portal and for the URI of the 42 application, you should set it to `https://<yourdomainname>/oauth/callback/42`.


## Usage

When you have set up the `.env` file, you can run the following commands to start the server:

```bash
docker compose up --build -d
```

That's it! You can now access the service on your domain name.

## 🍰 Contributing
Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

## Author
#### Elidjah Maugalem
- Github: [@Zekao](https://github.com/Zekao)
- Intra: [emaugale](https://profile.intra.42.fr/users/emaugale)

## Special Thanks

Thanks to [@Millefeuille42](https://github.com/Millefeuille42) for the help in order to refactor the code and make it more readable.
