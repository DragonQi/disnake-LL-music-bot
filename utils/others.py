from __future__ import annotations

import json
from inspect import iscoroutinefunction
from io import BytesIO
from typing import TYPE_CHECKING, Union, Optional
import disnake
from disnake.ext import commands
from utils.db import DBModel

if TYPE_CHECKING:
    from utils.client import BotCore


class Test:

    def is_done(self):
        return True

class CustomContext(commands.Context):
    bot: BotCore
    def __init__(self, prefix, view, bot: BotCore, message):
        super(CustomContext, self).__init__(prefix=prefix, view=view, bot=bot, message=message)
        self.response = Test()
        self.response.defer = self.defer
        self.user = self.author
        self.guild_id = self.guild.id
        self.store_message = None

    async def defer(self, ephemeral: bool = False):
        await self.trigger_typing()
        return

    async def send(self, *args, **kwargs):

        try:
            kwargs.pop("ephemeral")
        except:
            pass

        return await super().send(*args, **kwargs)

    async def reply(self, *args, **kwargs):

        try:
            kwargs.pop("ephemeral")
        except:
            pass

        return await super().reply(*args, **kwargs)


class ProgressBar:

    def __init__(
            self,
            position: Union[int, float],
            total: Union[int, float],
            bar_count: int = 10
    ):
        self.start = int(bar_count * (position / total))
        self.end = int(bar_count - self.start) - 1


class PlayerControls:
    add_song = "musicplayer_add_song"
    enqueue_fav = "musicplayer_enqueue_fav"
    play = "musicplayer_play"
    stop = "musicplayer_stop"
    pause_resume = "musicplayer_playpause"
    pause = "musicplayer_pause"
    resume = "musicplayer_resume"
    back = "musicplayer_back"
    skip = "musicplayer_skip"
    volume = "musicplayer_volume"
    shuffle = "musicplayer_shuffle"
    seek_to_start = "musicplayer_seek_to_start"
    readd = "musicplayer_readd"
    loop_mode = "musicplayer_loop_mode"
    queue = "musicplayer_queue"
    nightcore = "musicplayer_nightcore"
    help_button = "musicplayer_help"
    restrict_mode = "musicplayer_restrict_mode"


class EmbedPaginator(disnake.ui.View):

    def __init__(self, ctx: Union[CustomContext, disnake.MessageInteraction], embeds: list[disnake.Embed], *,timeout=180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.embeds = embeds
        self.current = 0
        self.max_page = len(embeds) - 1
        self.message: Optional[disnake.Message] = None

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:

        if interaction.author != self.ctx.author:
            await interaction.send(f"Только участник {self.ctx.author.mention} может использовать эти кнопки...")
            return False

        return True

    @disnake.ui.button(emoji='⬅️', style=disnake.ButtonStyle.grey)
    async def back(self, button, interaction: disnake.MessageInteraction):

        if self.current == 0:
            self.current = self.max_page
        else:
            self.current -= 1
        await interaction.response.edit_message(embed=self.embeds[self.current])

    @disnake.ui.button(emoji='➡️', style=disnake.ButtonStyle.grey)
    async def next(self, button, interaction: disnake.MessageInteraction):

        if self.current == self.max_page:
            self.current = 0
        else:
            self.current += 1
        await interaction.response.edit_message(embed=self.embeds[self.current])

    @disnake.ui.button(emoji='⏹️', style=disnake.ButtonStyle.red, label="Fechar")
    async def close(self, button, interaction: disnake.MessageInteraction):

        await interaction.message.delete()
        self.stop()

    async def on_timeout(self):

        try:
            await self.message.delete()
        except:
            pass

        self.stop()



def sync_message(bot: BotCore):
    app_commands_invite = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&scope=applications.commands"
    bot_invite = disnake.utils.oauth_url(bot.user.id, permissions=disnake.Permissions(bot.config['INVITE_PERMISSIONS']), scopes=('bot', 'applications.commands'))

    return f"`Если слэш-команды не отображаются,` [`кликните сюда`]({app_commands_invite}) `чтобы позволить мне " \
           "создавать слэш-команды на сервере.`\n\n" \
           "`Примечание. В некоторых случаях для появления/обновления команд со слешем может потребоваться до часа." \
           "серверы. Если вы хотите использовать слэш-команды сразу на сервере, вам придется " \
           f"выкинь меня с сервера и снова добавь через это` [`link`]({bot_invite})..."


def chunk_list(lst: list, amount: int):
    return [lst[i:i + amount] for i in range(0, len(lst), amount)]


async def check_cmd(cmd, inter: Union[disnake.Interaction, disnake.ModalInteraction, CustomContext]):

    """try:
        inter.application_command = cmd
        await cmd._max_concurrency.acquire(inter)
    except AttributeError:
        pass"""

    bucket = cmd._buckets.get_bucket(inter)  # type: ignore
    if bucket:
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(cooldown=bucket, retry_after=retry_after, type=cmd._buckets.type)

    if isinstance(inter, CustomContext):
        await cmd.can_run(inter)
        return

    for command_check in cmd.checks:
        c = (await command_check(inter)) if iscoroutinefunction(command_check) else command_check(inter)
        if not c:
            raise commands.CheckFailure()

    """try:
        chkcmd = list(cmd.children.values())[0]
    except (AttributeError, IndexError):
        try:
            chkcmd = inter.bot.get_slash_command(cmd.qualified_name.split()[-2])
        except IndexError:
            chkcmd = None

    if chkcmd:
        await check_cmd(chkcmd, inter)"""



async def send_message(
        inter: Union[disnake.Interaction, disnake.ApplicationCommandInteraction],
        text=None,
        *,
        embed: disnake.Embed = None,
        components: Optional[list] = None,
):

    # correção temporária usando variavel kwargs.
    kwargs = {}

    if embed:
        kwargs["embed"] = embed

    if inter.response.is_done() and isinstance(inter, disnake.AppCmdInter):
        await inter.edit_original_message(content=text, components=components, **kwargs)

    else:

        if components:
            kwargs["components"] = components

        await inter.send(text, ephemeral=True, **kwargs)


async def send_idle_embed(
        target: Union[disnake.Message, disnake.TextChannel, disnake.Thread, disnake.MessageInteraction],
        text="", *, bot: BotCore, force=False, guild_data: dict = None
):

    if isinstance(target, disnake.Thread) and isinstance(target.parent, disnake.ForumChannel):
        content = "Сообщение для запроса песни."
    else:
        content = None

    embed = disnake.Embed(description="**Присоединяйтесь к голосовому каналу и запросите песню здесь " +
                                      ("нет поста" if content else "на канале или в беседе ниже") +
                                      " (или нажмите кнопку ниже)**\n\n"
                                      "**Вы можете использовать имя или ссылку на поддерживаемый веб-сайт:**"
                                      " ```ansi\n[31;1mYoutube[0m, [33;1mSoundcloud[0m, [32;1mSpotify[0m, [34;1mTwitch[0m```\n",
                          color=bot.get_color(target.guild.me))

    if text:
        embed.description += f"**Последнее действие:** {text.replace('**', '')}\n"

    embed.set_thumbnail(target.guild.me.display_avatar.replace(size=256).url)

    if not guild_data:
        guild_data = await bot.get_data(target.guild.id, db_name=DBModel.guilds)

    components = []

    opts = [disnake.SelectOption(label=k, value=k, description=v.get('description')) for k, v in sorted(guild_data["player_controller"]["fav_links"].items(), key=lambda k: k)]

    if opts:
        components.append(
            disnake.ui.Select(
                placeholder="Серверные песни/плейлисты.",
                options=opts, custom_id="player_guild_pin",
                min_values=0, max_values=1
            )
        )

    components.extend(
        [
            disnake.ui.Button(
                emoji="🎶",
                custom_id=PlayerControls.add_song,
                label="Запросить песню"
            ),
            disnake.ui.Button(
                emoji="⭐",
                custom_id=PlayerControls.enqueue_fav,
                label="Добавить в избранное"
            )
        ]
    )

    if isinstance(target, disnake.MessageInteraction):
        await target.response.edit_message(embed=embed, content=content or None, components=components)
        message = target.message

    elif isinstance(target, disnake.Message):

        if guild_data["player_controller"]["channel"] != str(target.channel.id) and not force:
            return target

        if target.author == target.guild.me:
            await target.edit(embed=embed, content=None, components=components)
            message = target
        else:
            message = await target.channel.send(embed=embed, components=components)
    else:

        message = await target.send(embed=embed, components=components)

    return message


def string_to_file(txt, filename="result.txt"):
    if isinstance(txt, dict):
        txt = json.dumps(txt, indent=4, ensure_ascii=False)
    txt = BytesIO(bytes(str(txt), 'utf-8'))
    return disnake.File(fp=txt, filename=filename or "result.txt")
