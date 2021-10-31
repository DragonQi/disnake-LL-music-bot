import disnake
from disnake.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
from json import load
from utils.music.local_lavalink import run_lavalink
from utils.client import BotCore


try:
    with open('config.json', encoding='utf-8') as f:
        config = load(f)
except FileNotFoundError:
    config = {}

if config['lavalink']['local']['start_local_lavalink']:
    run_lavalink(
        lavalink_file_url=config['lavalink']['local']['lavalink_file_url'],
        lavalink_ram_limit=config['lavalink']['local']['lavalink_ram_limit'],
        lavalink_additional_sleep=config['lavalink']['local']['lavalink_additional_sleep'],
    )

load_dotenv()

if os.getenv('KEEP_ALIVE') != "false":
    keep_alive()

intents = disnake.Intents.default()
intents.members = True
intents.presences = True

mongo_key = os.environ.get("MONGO")

if not mongo_key:
    print("Token do mongoDB não configurado! funções que requer database vão estar indisponíveis.")


bot = BotCore(
    command_prefix=commands.when_mentioned_or(os.environ.get('DEFAULT_PREFIX'), '!!'),
    case_insensitive=True,
    intents=intents,
    test_guilds=[],
    sync_commands=False,
    sync_commands_on_cog_unload=False,
    config=config,
    db_name="botdiscord",
    mongo=mongo_key
)


@bot.event
async def on_ready():
    print(f'{bot.user} [{bot.user.id}] Online.')


@bot.before_slash_command_invoke
@bot.before_user_command_invoke
@bot.before_message_command_invoke
async def before_interaction(inter: disnake.ApplicationCommandInteraction):
    if bot.db:
        #inter.user_data = await bot.db.get_data(inter.author.id, db_name="users")
        inter.guild_data = await bot.db.get_data(inter.guild.id, db_name="guilds")
    else:
        #inter.user_data = None
        inter.guild_data = None


bot.load_modules()

bot.run(os.environ['TOKEN'])
