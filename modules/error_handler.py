from __future__ import annotations
import disnake
from disnake.ext import commands
from aiohttp import ClientSession
import asyncio
import traceback
from utils.music.converters import URL_REG
from utils.music.errors import parse_error
from utils.others import send_message, CustomContext, string_to_file
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from utils.client import BotCore


class ErrorHandler(commands.Cog):

    def __init__(self, bot: BotCore):
        self.bot = bot
        self.components = []
        self.webhook_max_concurrency = commands.MaxConcurrency(1, per=commands.BucketType.guild, wait=True)

        if self.bot.config["ERROR_REPORT_WEBHOOK"]:
            self.components.append(
                disnake.ui.Button(
                    label="Сообщение об ошибке",
                    custom_id="report_error",
                    emoji="⚠"
                )
            )

        if self.bot.config["SUPPORT_SERVER"]:
            self.components.append(
                disnake.ui.Button(
                    label="Сервер поддержки",
                    url=self.bot.config["SUPPORT_SERVER"]
                )
            )

    @commands.Cog.listener('on_interaction_player_error')
    async def on_inter_player_error(self, inter: disnake.AppCmdInter, error: Exception):

        await self.process_interaction_error(inter=inter, error=error)

    """@commands.Cog.listener('on_user_command_completion')
    @commands.Cog.listener('on_message_command_completion')
    @commands.Cog.listener('on_slash_command_completion')
    async def interaction_command_completion(self, inter: disnake.AppCmdInter):

        try:
            await inter.application_command._max_concurrency.release(inter)
        except:
            pass


    @commands.Cog.listener("on_command_completion")
    async def legacy_command_completion(self, ctx: CustomContext):

        try:
            await ctx.command._max_concurrency.release(ctx.message)
        except:
            pass"""

    @commands.Cog.listener('on_user_command_error')
    @commands.Cog.listener('on_message_command_error')
    @commands.Cog.listener('on_slash_command_error')
    async def on_interaction_command_error(self, inter: disnake.AppCmdInter, error: Exception):

        await self.process_interaction_error(inter=inter, error=error)

    async def process_interaction_error(self, inter: disnake.AppCmdInter, error: Exception):

        """if not isinstance(error, commands.MaxConcurrencyReached):
            try:
                await inter.application_command._max_concurrency.release(inter)
            except:
                pass"""

        error_msg, full_error_msg = parse_error(inter, error)

        kwargs = {}
        components = None
        send_webhook = False

        if inter.guild.me.guild_permissions.embed_links:

            kwargs["embed"] = disnake.Embed(color=disnake.Colour.red())
            kwargs["text"] = inter.author.mention

            if not error_msg:

                kwargs["embed"].title = "Произошла ошибка в команде:"
                kwargs["embed"].description = f"```py\n{repr(error)[:2030].replace(self.bot.http.token, 'mytoken')}```"

                if self.bot.config["AUTO_ERROR_REPORT_WEBHOOK"]:
                    send_webhook = True
                    kwargs["embed"].description += " `Мой разработчик будет уведомлен о проблеме.`"

                else:

                    components = self.components

            else:
                kwargs["embed"].description = error_msg

        else:

            kwargs["text"] = inter.author.mention

            if not error_msg:
                components = self.components
                kwargs["text"] += " произошла ошибка в команде: ```py\n" \
                                  f"{repr(error)[:2030].replace(self.bot.http.token, 'mytoken')}```"
            else:
                components = None
                kwargs["text"] += f": {error}"

        await send_message(inter, components=components, **kwargs)

        if not send_webhook:
            return

        try:
            await self.webhook_max_concurrency.acquire(inter)

            await self.send_webhook(
                embed=self.build_report_embed(inter),
                file=string_to_file(full_error_msg, "error_traceback_interaction.txt")
            )

            await asyncio.sleep(20)

            await self.webhook_max_concurrency.release(inter)

        except:
            traceback.print_exc()

    @commands.Cog.listener("on_command_error")
    async def on_legacy_command_error(self, ctx: CustomContext, error: Exception):

        """if not isinstance(error, commands.MaxConcurrencyReached):
            try:
                await ctx.command._max_concurrency.release(ctx.message)
            except:
                pass"""

        if isinstance(error, commands.CommandNotFound):
            return

        error_msg, full_error_msg = parse_error(ctx, error)
        kwargs = {}
        send_webhook = False
        components = None

        if ctx.guild.me.guild_permissions.embed_links:

            kwargs["embed"] = disnake.Embed(color=disnake.Colour.red())
            kwargs["content"] = ctx.author.mention

            if not error_msg:
                kwargs["embed"].title = "Произошла ошибка в команде:"
                kwargs["embed"].description = f"```py\n{repr(error)[:2030].replace(self.bot.http.token, 'mytoken')}```"
                if self.bot.config["AUTO_ERROR_REPORT_WEBHOOK"]:
                    send_webhook = True
                    kwargs["embed"].description += " `Мой разработчик будет уведомлен о проблеме.`"
                else:
                    components = self.components

            else:
                kwargs["embed"].description = error_msg

        else:

            kwargs["content"] = ctx.author.mention

            if not error_msg:
                kwargs["content"] += " Произошла ошибка в команде: ```py\n" \
                                     f"{repr(error)[:2030].replace(self.bot.http.token, 'mytoken')}```"
                if self.bot.config["AUTO_ERROR_REPORT_WEBHOOK"]:
                    send_webhook = True
                    kwargs["content"] += " `Мой разработчик будет уведомлен о проблеме.`"
                else:
                    components = self.components
            else:
                components = None
                kwargs["content"] += f": {error}"

        try:
            delete_time = error.delete_original
        except AttributeError:
            delete_time = None

        try:
            if error.self_delete and ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()
        except:
            pass

        await ctx.send(components=components, delete_after=delete_time, **kwargs)

        if not send_webhook:
            return

        try:
            await self.webhook_max_concurrency.acquire(ctx)

            await self.send_webhook(
                embed=self.build_report_embed(ctx),
                file=string_to_file(full_error_msg, "error_traceback_prefixed.txt")
            )

            await asyncio.sleep(20)

            await self.webhook_max_concurrency.release(ctx)

        except:
            traceback.print_exc()

    @commands.Cog.listener("on_button_click")
    async def on_error_report(self, inter: disnake.MessageInteraction):

        if inter.data.custom_id != "report_error":
            return

        if str(inter.author.id) not in inter.message.content:
            await inter.send(f"Только пользователь {inter.message.content} может использовать эту кнопку", ephemeral=True)
            return

        await inter.response.send_modal(
            title="Сообщить об ошибке",
            custom_id=f"error_report_submit_{inter.message.id}",
            components=[
                disnake.ui.TextInput(
                    style=disnake.TextInputStyle.long,
                    label="Подробности",
                    custom_id="error_details",
                    max_length=1900,
                    required=True
                ),
                disnake.ui.TextInput(
                    style=disnake.TextInputStyle.short,
                    label="Ссылка на фото/скриншот ошибки (опционально)",
                    custom_id="image_url",
                    max_length=300,
                    required=False
                )
            ]
        )

    @commands.Cog.listener("on_modal_submit")
    async def on_report_submit(self, inter: disnake.ModalInteraction):

        if not inter.custom_id.startswith("error_report_submit"):
            return

        if not inter.message.embeds:
            await inter.response.edit_message(
                embed=disnake.Embed(
                    title="Вставка сообщения была удалена!",
                    description=inter.text_values["error_details"]
                ), view=None
            )
            return

        image_url = inter.text_values["image_url"]

        if image_url and not URL_REG.match(image_url):
            await inter.send(
                embed=disnake.Embed(
                    title="Неверная ссылка на изображение!",
                    description=inter.text_values["error_details"]
                ), ephemeral=True
            )
            return

        embed = disnake.Embed(
            color=self.bot.get_color(inter.guild.me),
            description=inter.text_values["error_details"],
            title="Сообщить об ошибке"
        )

        embed.add_field(name="Log:", value=inter.message.embeds[0].description)

        await inter.response.edit_message(
            embed=disnake.Embed(
                description="**Репорт ошибки успешно отправлен**",
                color=self.bot.get_color(inter.guild.me)
            ), view=None
        )

        try:
            user_avatar = inter.author.avatar.with_static_format("png").url
        except AttributeError:
            user_avatar = inter.author.avatar.url

        embed.set_author(name=f"Сообщение об ошибке: {inter.author} - {inter.author.id}", icon_url=user_avatar)

        guild_txt = f"Servidor: {inter.guild.name} [{inter.guild.id}]"

        try:
            embed.set_footer(text=guild_txt, icon_url=inter.guild.icon.with_static_format("png").url)
        except AttributeError:
            embed.set_footer(text=guild_txt)

        if image_url:
            embed.set_image(url=image_url)

        await self.send_webhook(embed=embed)

    def build_report_embed(self, ctx):

        embed = disnake.Embed(
            title="Произошла ошибка на сервере:",
            color=self.bot.get_color(ctx.guild.me),
            timestamp=disnake.utils.utcnow()
        )
        embed.set_footer(
            text=f"{ctx.author} [{ctx.author.id}]",
            icon_url=ctx.author.display_avatar.with_static_format("png").url
        )
        embed.add_field(
            name="Servidor:", inline=False,
            value=f"```\n{disnake.utils.escape_markdown(ctx.guild.name)}\nID: {ctx.guild.id}```"
        )
        embed.add_field(
            name="Canal de texto:", inline=False,
            value=f"```\n{disnake.utils.escape_markdown(ctx.channel.name)}\nID: {ctx.channel.id}```"
        )

        if vc := ctx.author.voice:
            embed.add_field(
                name="Голосовой канал (пользователь):", inline=False,
                value=f"```\n{disnake.utils.escape_markdown(vc.channel.name)}" +
                      (f" ({len(vc.channel.voice_states)}/{vc.channel.user_limit})"
                       if vc.channel.user_limit else "") + f"\nID: {vc.channel.id}```"
            )

        if vcbot := ctx.guild.me.voice:
            if vcbot.channel != vc.channel:
                embed.add_field(
                    name="Голосовой канал (бот):", inline=False,
                    value=f"{vc.channel.name}" +
                          (f" ({len(vc.channel.voice_states)}/{vc.channel.user_limit})"
                           if vc.channel.user_limit else "") + f"\nID: {vc.channel.id}```"
                )

        try:

            embed.description = f"**Слэш команда:**```\n{ctx.data.name}``` "

            if ctx.filled_options:
                embed.description += "**Опции**```\n" + \
                                     "\n".join(f"{k} -> {disnake.utils.escape_markdown(v)}"
                                               for k, v in ctx.filled_options.items()) + "```"

        except AttributeError:
            if self.bot.intents.message_content and not ctx.author.bot:
                embed.description = f"**Команда:**```\n" \
                                    f"{ctx.message.content.replace(str(self.bot.user.mention), f'@{ctx.guild.me.display_name}')}" \
                                    f"```"

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.with_static_format("png").url)

        return embed

    async def send_webhook(
            self,
            content: str = None,
            embed: Optional[disnake.Embed] = None,
            file: Optional[disnake.File] = None
    ):

        kwargs = {
            "username": self.bot.user.name,
            "avatar_url": self.bot.user.display_avatar.replace(static_format='png').url,
        }

        if content:
            kwargs["content"] = content

        if embed:
            kwargs["embed"] = embed

        if file:
            kwargs["file"] = file

        async with ClientSession() as session:
            webhook = disnake.Webhook.from_url(self.bot.config["AUTO_ERROR_REPORT_WEBHOOK"], session=session)
            await webhook.send(**kwargs)


def setup(bot: BotCore):
    bot.add_cog(ErrorHandler(bot))
