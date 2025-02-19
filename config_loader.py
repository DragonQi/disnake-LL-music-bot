from json import load
from dotenv import dotenv_values
from os import environ

bools = {
    "true": True,
    "false": False,
    "none": None
}

DEFAULT_CONFIG = {
    "DEFAULT_PREFIX": "!!!",
    "AUTO_SYNC_COMMANDS": True,
    "OWNER_IDS": "",
    "COMMAND_LOG": False,
    "EMBED_COLOR": None,
    "BOT_ADD_REMOVE_LOG": '',
    "ERROR_REPORT_WEBHOOK": '',
    "AUTO_ERROR_REPORT_WEBHOOK": '',
    "INTERACTION_COMMAND_ONLY": False,
    "PRESENCE_INTERVAL": 900,
    "SOURCE_REPO": "https://github.com/zRitsu/disnake-LL-music-bot.git",
    "HIDE_SOURCE_OWNER": False,
    "SUPPORT_SERVER": "",
    "ADDITIONAL_BOT_IDS": "",
    "INVITE_PERMISSIONS": 534735285328,
    "ENABLE_LOGGER": False,

    ################
    ### Database ###
    ################
    "MONGO": "",

    #########################
    ### Sistema de música ###
    #########################
    "AUTO_DOWNLOAD_LAVALINK_SERVERLIST": False,
    "LAVALINK_SERVER_LIST": "https://github.com/zRitsu/LL-binaries/releases/download/0.0.1/lavalink.ini",
    "DEFAULT_SKIN": "default",
    "VOTE_SKIP_AMOUNT": 3,
    "IDLE_TIMEOUT": 180,
    "RUN_RPC_SERVER": True,
    "RPC_SERVER": "ws://localhost:$PORT/ws",
    "MAX_USER_FAVS": 10,
    "USER_FAV_MAX_NAME_LENGTH": 35,
    "USER_FAV_MAX_URL_LENGTH": 90,
    "HINT_RATE": 4,
    "IGNORE_SKINS": '',
    "GUILD_DEAFEN_WARN": True,

    ##############################################
    ### Sistema de música - Suporte ao spotify ###
    ##############################################
    "SPOTIFY_CLIENT_ID": '',
    "SPOTIFY_CLIENT_SECRET": '',

    ##################################################
    ### Sistema de música - Local lavalink stuffs: ###
    ##################################################
    "RUN_LOCAL_LAVALINK": False,
    "LAVALINK_ADDITIONAL_SLEEP": 0,
    "LAVALINK_INITIAL_RAM": 30,
    "LAVALINK_RAM_LIMIT": 120,
    "LAVALINK_CPU_CORES": 2,
    "LAVALINK_FILE_URL": "https://github.com/zRitsu/LL-binaries/releases/download/0.0.1/Lavalink.jar",

    ##########################
    ##### Bot presences: #####
    ##########################
    "LISTENING_PRESENCES": "",
    "WATCHING_PRESENCES": "",
    "PLAYING_PRESENCES": "",

    ###############
    ### Intents ###
    ###############
    "BANS_INTENT": False,
    "DM_MESSAGES_INTENT": False,
    "DM_REACTIONS_INTENT": False,
    "DM_TYPING_INTENT": False,
    "GUILD_MESSAGES_INTENT": True,
    "GUILD_REACTIONS_INTENT": False,
    "GUILD_SCHEDULED_EVENTS_INTENT": False,
    "GUILD_TYPING_INTENT": False,
    "EMOJIS_AND_STICKERS_INTENT": True,
    "GUILDS_INTENT": True,
    "INTEGRATIONS_INTENT": True,
    "INVITES_INTENT": True,
    "VOICE_STATES_INTENT": True,
    "WEBHOOKS_INTENT": False,

    ##########################
    ### Privileged Intents ###
    ##########################
    "MEMBERS_INTENT": True,
    "PRESENCES_INTENT": False,
    "MESSAGE_CONTENT_INTENT": True,
}


def load_config():

    CONFIG = dict(DEFAULT_CONFIG)

    for cfg in list(CONFIG) + ["TOKEN", "MONGO"]:
        try:
            CONFIG[cfg] = environ[cfg]
        except KeyError:
            continue

    for env in environ:
        if env.lower().startswith(("token_bot_", "test_guilds_", "lavalink_node_")):
            CONFIG[env] = environ[env]

    try:
        with open("config.json") as f:
            CONFIG.update(load(f))
    except FileNotFoundError:
        pass

    try:
        CONFIG.update(dotenv_values())
    except:
        pass

    if CONFIG["EMBED_COLOR"] is False:
        CONFIG["EMBED_COLOR"] = None

    # converter strings que requer número int.
    for i in [
        "MAX_USER_FAVS",
        "IDLE_TIMEOUT",
        "VOTE_SKIP_AMOUNT",
        "LAVALINK_ADDITIONAL_SLEEP",
        "LAVALINK_INITIAL_RAM",
        "LAVALINK_RAM_LIMIT",
        "LAVALINK_CPU_CORES",
        "USER_FAV_MAX_NAME_LENGTH",
        "USER_FAV_MAX_URL_LENGTH",
        "PRESENCE_INTERVAL",
        "HINT_RATE",
        "INVITE_PERMISSIONS"
    ]:
        try:
            CONFIG[i] = int(CONFIG[i])
        except ValueError:
            raise Exception(f"Você usou uma configuração inválida! {i}: {CONFIG[i]}")

    # converter strings que requer valor bool/nulo.
    for i in [
        "AUTO_SYNC_COMMANDS",
        "EMBED_COLOR",
        "HIDE_SOURCE_OWNER",
        "INTERACTION_COMMAND_ONLY",
        "RUN_LOCAL_LAVALINK",
        "COMMAND_LOG",
        "RUN_RPC_SERVER",
        "AUTO_DOWNLOAD_LAVALINK_SERVERLIST",
        "ENABLE_LOGGER",
        "GUILD_DEAFEN_WARN",

        "BANS_INTENT",
        "DM_MESSAGES_INTENT",
        "DM_REACTIONS_INTENT",
        "DM_TYPING_INTENT",
        "GUILD_MESSAGES_INTENT",
        "GUILD_REACTIONS_INTENT",
        "GUILD_SCHEDULED_EVENTS_INTENT",
        "GUILD_TYPING_INTENT",
        "EMOJIS_AND_STICKERS_INTENT",
        "GUILDS_INTENT",
        "INTEGRATIONS_INTENT",
        "INVITES_INTENT",
        "VOICE_STATES_INTENT",
        "WEBHOOKS_INTENT",

        "MEMBERS_INTENT",
        "PRESENCES_INTENT",
        "MESSAGE_CONTENT_INTENT",
    ]:
        if CONFIG[i] in (True, False, None):
            continue

        try:
            CONFIG[i] = bools[CONFIG[i]]
        except KeyError:
            raise Exception(f"Você usou uma configuração inválida! {i}: {CONFIG[i]}")

    CONFIG["RPC_SERVER"] = CONFIG["RPC_SERVER"].replace("$PORT", environ.get("PORT", "8080"))

    if CONFIG["PRESENCE_INTERVAL"] < 300:
        CONFIG["PRESENCE_INTERVAL"] = 300

    if CONFIG["IDLE_TIMEOUT"] < 30:
        CONFIG["IDLE_TIMEOUT"] = 30

    return CONFIG
