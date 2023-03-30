# SubRedBot

A simple discord bot that retrieves images/GIF links from reddit posts


# Installation

- Clone the repository
```bash
git clone https://github.com/BoredRyuzaki/SubRedBot.git
```

- Move into the directory and install dependencies using [poetry]()
```bash
cd SubRedBot
poetry install
```

- Add the `.env` file to the project root
```bash
touch .env
```
It should look something like this
```env
REDDIT_CLIENT_ID=<YOUR_CLIENT_ID>
REDDIT_CLIENT_SECRET=<YOUR_CLIENT_SECRET>
REDDIT_USER_AGENT=<USER_AGENT_NAME>
DISCORD_TOKEN=<YOUR_DISCORD_BOT_TOKEN>
```

- Run it!
```bash
poetry run python src/bot.py
```
