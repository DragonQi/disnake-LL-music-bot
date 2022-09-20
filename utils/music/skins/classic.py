from ..models import LavalinkPlayer
import disnake
from ..converters import fix_characters, time_format
import itertools


def load(player: LavalinkPlayer) -> dict:

    data = {
        "content": None,
        "embeds": []
    }

    embed = disnake.Embed(color=player.bot.get_color(player.guild.me), description="")

    if not player.static:
        embed_top = disnake.Embed(
            color=player.bot.get_color(player.guild.me),
            description=f"> [**{player.current.title}**]({player.current.uri})"
        )
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/554468640942981147/937918500784197632/rainbow_bar.gif"
        )

        embed_top.set_image(
            url="https://cdn.discordapp.com/attachments/554468640942981147/937918500784197632/rainbow_bar.gif"
        )

        embed_top.set_thumbnail(url=player.current.thumb)

    else:
        embed.description = f"[**{player.current.title}**]({player.current.uri})\n\n"
        embed.set_image(url=player.current.thumb)
        embed_top = None

    if not player.paused:
        (embed_top or embed).set_author(
            name="Играть сейчас:",
            icon_url="https://cdn.discordapp.com/attachments/480195401543188483/895862881105616947/music_equalizer.gif"
        )
    else:
        (embed_top or embed).set_author(
            name="На паузе:",
            icon_url="https://cdn.discordapp.com/attachments/480195401543188483/896013933197013002/pause.png"
        )

    if player.current.is_stream:
        duration = "🔴 **⠂Livestream**"
    else:
        duration = f"⏰ **⠂Продолжительность** `{time_format(player.current.duration)}`"

    txt = f"{duration}\n" \
          f"💠 **⠂Автор**: `{player.current.author}`\n" \
          f"🎧 **⠂Заказан:** <@{player.current.requester}>\n" \

    if player.current.playlist_name:
        txt += f"📑 **⠂Playlist:** [`{fix_characters(player.current.playlist_name, limit=20)}`]({player.current.playlist_url})\n"

    txt += f"🔊 **⠂Громкость:** `{player.volume}%`\n"

    if player.restrict_mode:
        txt += "🔒 **⠂Ограниченный режим: `активирован`\n"

    if player.command_log:
        txt += f"{player.command_log_emoji} **⠂Последнее взаимодействие:** {player.command_log}\n"

    if qsize := len(player.queue):

        if player.static:

            data["content"] = "**Песни в очереди:**\n```ожидают\n" + \
                              "\n".join(f"[0;33m{(n+1):02}[0m [0;34m[{time_format(t.duration) if not t.is_stream else '🔴 stream'}][0m [0;36m{fix_characters(t.title, 45)}[0m" for n, t in enumerate(
                                  itertools.islice(player.queue, 15)))

            if (qsize := len(player.queue)) > 15:
                data["content"] += f"\n\n[0;37mE mais[0m [0;35m{qsize}[0m [0;37mmúsicas(s).[0m"

            data["content"] += "```"

        else:
            txt += "```ожидают\n[0;33mПредстоящие песни:[0m```" + "\n".join(
                f"`{(n + 1):02}) [{time_format(t.duration) if t.duration else '🔴 Livestream'}]` "
                f"[`{fix_characters(t.title, 31)}`]({t.uri})" for n, t in enumerate(itertools.islice(player.queue, 3))
            )

            if qsize > 3:
                txt += f"\n`╚══════ И более {qsize - 3} песни(я) ══════╝`"

    embed.description += txt

    if player.current_hint:
        embed.set_footer(text=f"💡 Подсказка: {player.current_hint}")

    data["embeds"] = [embed_top, embed] if embed_top else [embed]

    return data
