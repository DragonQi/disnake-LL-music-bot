import datetime
from typing import Union
import disnake
import re
import json
from user_agent import generate_user_agent
from utils.db import DBModel

URL_REG = re.compile(r'https?://(?:www\.)?.+')
YOUTUBE_VIDEO_REG = re.compile(r"(https?://)?(www\.)?youtube\.(com|nl)/watch\?v=([-\w]+)")

replaces = [
    ('&quot;', '"'),
    ('&amp;', '&'),
    ('(', '\u0028'),
    (')', '\u0029'),
    ('[', '【'),
    (']', '】'),
    ("  ", " "),
    ("*", '"'),
    ("_", ' '),
    ("{", "\u0028"),
    ("}", "\u0029"),
    ("`", "'")
]

perms_translations = {
    "add_reactions": "Adicionar Reações",
    "administrator": "Administrador",
    "attach_files": "Anexar Arquivos",
    "ban_members": "Banir Membros",
    "change_nickname": "Alterar apelido",
    "connect": "Conectar em canal de voz",
    "create_instant_invite": "Criar convite instantâneo",
    "create_private_threads": "Criar Tópicos Privado",
    "create_public_threads": "Criar Tópicos Públicos",
    "deafen_members": "Ensurdecer membros",
    "embed_links": "Embutir links",
    "kick_members": "Expulsar Membros",
    "manage_channels": "Gerenciar Canais",
    "manage_emojis_and_stickers": "Gerenciar Emojis e Figurinhas",
    "manage_events": "Gerenciar Eventos",
    "manage_guild": "Gerenciar Servidor",
    "manage_messages": "Gerenciar Mensagens",
    "manage_nicknames": "Gerenciar Apelidos",
    "manage_roles": "Gerenciar Cargos",
    "manage_threads": "Gerenciar Tópicos",
    "manage_webhooks": "Gerenciar Webhooks",
    "mention_everyone": "Marcar @everyone e @here",
    "moderate_members": "Moderar membros",
    "move_members": "Mover membros",
    "mute_members": "Silenciar membros",
    "priority_speaker": "Prioridade para falar",
    "read_message_history": "Mostrar histórico de mensagens",
    "request_to_speak": "Pedir para falar",
    "send_messages": "Enviar mensagem",
    "send_messages_in_threads": "Enviar mensagem em tópicos",
    "send_tts_messages": "Enviar mensagens de texto-a-voz",
    "speak": "Falar em canal de voz",
    "stream": "Transmitir",
    "use_application_commands": "Usar comandos de aplicações/bots",
    "use_embedded_activities": "Usar atividades ",
    "use_external_emojis": "Usar Emojis Externos",
    "use_external_stickers": "Usar Figurinhas Externas",
    "use_voice_activation": "Usar detecção de voz automática",
    "view_audit_log": "Visualizar registro de auditória",
    "view_channel": "Ver canal",
    "view_guild_insights": "Ver análises do servidor"
}

u_agent = generate_user_agent()


async def node_suggestions(inter, query: str):
    try:
        node = inter.bot.music.players[inter.guild.id].node
    except KeyError:
        node = None

    if not query:
        return [n.identifier for n in inter.bot.music.nodes.values() if n != node and n.available and n.is_available]

    return [n.identifier for n in inter.bot.music.nodes.values() if n != node
            and query.lower() in n.identifier.lower() and n.available and n.is_available]


async def google_search(bot, query: str, *, max_entries: int = 20) -> list:
    if URL_REG.match(query):
        return [query]

    async with bot.session.get(
            f"http://suggestqueries.google.com/complete/search?client=chrome&ds=yt&q={query}",
            headers={'User-Agent': u_agent}) as r:
        return json.loads(await r.text())[1][:max_entries]


async def search_suggestions(inter, query: str):
    if not query:
        return []

    if not inter.author.voice:
        return []

    return await google_search(inter.bot, query)


def queue_tracks(inter, query: str):
    if not inter.author.voice:
        return

    try:
        player = inter.bot.music.players[inter.guild.id]
    except KeyError:
        return

    return [f"{track.title}"[:100] for n, track in enumerate(player.queue) if query.lower() in track.title.lower()][:20]


def queue_playlist(inter, query: str):
    if not inter.author.voice:
        return

    try:
        player = inter.bot.music.players[inter.guild.id]
    except KeyError:
        return

    return list(set([track.playlist_name for track in player.queue if track.playlist_name and
                     query.lower() in track.playlist_name.lower()]))[:20]


async def fav_list(inter, query: str, *, prefix=""):
    return sorted([f"{prefix}{favname}" for favname in
                   (await inter.bot.get_global_data(inter.author.id, db_name=DBModel.users))["fav_links"]
                   if not query or query.lower() in favname.lower()][:20])


async def pin_list(inter, query: str, *, prefix=""):
    return sorted([f"{prefix}{pinname}" for pinname in
                   (await inter.bot.get_data(inter.guild.id, db_name=DBModel.guilds))["player_controller"]["fav_links"]
                   if not query or query.lower() in pinname.lower()][:20])


async def fav_add_autocomplete(inter, query: str):
    favs: list = await fav_list(inter, query, prefix="> fav: ")

    if not inter.author.voice or not query or (favs_size := len(favs)) >= 20:
        return favs[:20]

    return await google_search(inter.bot, query, max_entries=20 - favs_size) + favs


def queue_author(inter, query):
    if not query:
        return

    if not inter.author.voice:
        return

    try:
        player = inter.bot.music.players[inter.guild.id]
    except KeyError:
        return

    return list(set([track.author for track in player.queue if query.lower() in track.author.lower()]))[:20]


def seek_suggestions(inter, query):
    if query:
        return

    try:
        player = inter.bot.music.players[inter.guild.id]
    except KeyError:
        return

    if not player.current or player.current.is_stream:
        return

    seeks = []

    if player.current.duration >= 90000:
        times = [int(n * 0.5 * 10) for n in range(20)]
    else:
        times = [int(n * 1 * 10) for n in range(20)]

    for p in times:
        percent = percentage(p, player.current.duration)
        seeks.append(f"{time_format(percent)} | {p}%")

    return seeks


def get_button_style(enabled: bool, red=True):
    if enabled:
        if red:
            return disnake.ButtonStyle.red
        return disnake.ButtonStyle.green
    return disnake.ButtonStyle.grey


def fix_characters(text: str, limit: int = 0):
    for r in replaces:
        text = text.replace(r[0], r[1])

    if limit:
        text = f"{text[:limit]}..." if len(text) > limit else text

    return text


def time_format(milliseconds: Union[int, float], use_names: bool = False) -> str:
    minutes, seconds = divmod(int(milliseconds / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if use_names:

        times = []

        for time_, name in (
                (days, "dia"),
                (hours, "hora"),
                (minutes, "minuto"),
                (seconds, "segundo")
        ):
            if not time_:
                continue

            times.append(f"{time_} {name}" + ("s" if time_ > 1 else ""))

        try:
            last_time = times.pop()
        except IndexError:
            last_time = None
            times = ["1 segundo"]

        strings = ", ".join(t for t in times)

        if last_time:
            strings += f" e {last_time}" if strings else last_time

    else:

        strings = f"{minutes:02d}:{seconds:02d}"

        if hours:
            strings = f"{hours}:{strings}"

        if days:
            strings = (f"{days} dias" if days > 1 else f"{days} dia") + (f", {strings}" if strings != "00:00" else "")

    return strings


time_names = ["seconds", "minutes", "hours"]


def string_to_seconds(time):
    try:

        times = reversed(time.split(':'))
        time_dict = {}

        for n, t in enumerate(times):
            time_dict[time_names[n]] = int(t)

        return datetime.timedelta(**time_dict).total_seconds()

    except:
        return


def percentage(part, whole):
    return int((part * whole) / 100.0)


def queue_track_index(inter: disnake.AppCmdInter, query: str, check_all: bool = False):
    player = inter.bot.music.players[inter.guild.id]

    query_split = query.lower().split()

    tracklist = []

    for counter, track in enumerate(player.queue):

        track_title = track.title.lower().split()

        q_found = 0

        for q in query_split:
            for t in track_title:
                if q in t:
                    q_found += 1
                    track_title.remove(t)
                    break

        if q_found == len(query_split):

            tracklist.append((counter, track,))
            if not check_all:
                break

    return tracklist
