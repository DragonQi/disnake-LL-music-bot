from __future__ import annotations
from io import BytesIO
import json
import disnake
from disnake.ext import commands
from typing import TYPE_CHECKING, Union
from utils.music.converters import URL_REG, pin_list
from utils.music.errors import GenericError
from utils.music.models import LavalinkPlayer
from utils.others import send_idle_embed
from utils.db import DBModel

if TYPE_CHECKING:
    from utils.client import BotCore


class PinManager(commands.Cog):

    def __init__(self, bot: BotCore):
        self.bot = bot

    desc_prefix = "📌 [Плейлист сервера] 📌 | "


    async def process_idle_embed(self, guild: disnake.Guild):
        guild_data = await self.bot.get_data(guild.id, db_name=DBModel.guilds)

        try:
            player: LavalinkPlayer = self.bot.music.players[guild.id]
            if not player.current:
                await player.process_idle_message()
            return
        except KeyError:
            pass

        try:
            channel = self.bot.get_channel(int(guild_data["player_controller"]["channel"]))
            message = await channel.fetch_message(int(guild_data["player_controller"]["message_id"]))

        except:
            return

        await send_idle_embed(message or channel, bot=self.bot, guild_data=guild_data)

    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.slash_command(
        name=disnake.Localized("pin", data={disnake.Locale.pt_BR: "server_playlist"}),
        default_member_permissions=disnake.Permissions(manage_guild=True)
    )
    async def pin(self, inter: disnake.AppCmdInter):
        pass

    @pin.sub_command(
        name=disnake.Localized("add", data={disnake.Locale.pt_BR: "adicionar"}),
        description=f"{desc_prefix}Adicionar um link para lista de fixos do player."
    )
    async def add(
            self,
            inter: disnake.AppCmdInter,
            name: str = commands.Param(name="nome", description="Имя для ссылки."),
            url: str = commands.Param(name="link", description="Ссылка (рекомендуется плейлист)."),
            description: str = commands.Param(name="descrição", description="Описание ссылки.", default="")
    ):

        if "> fav:" in name.lower():
            raise GenericError("Вы не можете добавить элемент, содержащий это имя: **> fav:**")

        if not URL_REG.match(url):
            raise GenericError("**Вы не добавили действующую ссылку...**")

        if len(name) > 25:
            raise GenericError("**Имя не может превышать 25 символов.**")

        if len(description) > 50:
            raise GenericError("**Описание не может превышать 50 символов.**")

        if len(url) > (max_url_chars:=self.bot.config["USER_FAV_MAX_URL_LENGTH"]):
            raise GenericError(f"**Максимально допустимое количество символов в ссылке: {max_url_chars}**")

        await inter.response.defer(ephemeral=True)

        guild_data = await self.bot.get_data(inter.guild.id, db_name=DBModel.guilds)

        if len(guild_data["player_controller"]["fav_links"]) > 25:
            raise GenericError(f"**Превышено количество ссылок! Разрешено: 25.**")

        if not guild_data["player_controller"]["channel"] or not self.bot.get_channel(int(guild_data["player_controller"]["channel"])):
            raise GenericError("**На сервере не настроен плеер! Используйте команду /setup**")

        guild_data["player_controller"]["fav_links"][name] = {
            "url": url,
            "description": description
        }

        await self.bot.update_data(inter.guild.id, guild_data, db_name=DBModel.guilds)

        await inter.edit_original_message(embed=disnake.Embed(description="**Ссылка успешно добавлена/обновлена в значках плеера!\n"
                         "Участники могут использовать его непосредственно в плеере-контроллере, когда он не используется.**", color=self.bot.get_color(inter.guild.me)))

        await self.process_idle_embed(inter.guild)

    @pin.sub_command(
        name=disnake.Localized("edit", data={disnake.Locale.pt_BR: "редактирование"}),
        description=f"{desc_prefix}Редактировать элемент из списка фиксированных ссылок сервера"
    )
    async def edit(
            self,
            inter: disnake.AppCmdInter,
            item: str = commands.Param(autocomplete=pin_list, description="элемент для редактирования."), *,
            name: str = commands.Param(name="novo_nome", default="", description="Новое имя для ссылки."),
            url: str = commands.Param(name="novo_link", default="", description="Новая ссылка для выбранного элемента."),
            description: str = commands.Param(name="descrição", description="Описание ссылки", default="")
    ):

        if not name and not url and not description:
            raise GenericError("**Вы не указали ни один из необязательных элементов...**")

        if "> fav:" in name.lower():
            raise GenericError("Вы не должны включать это имя: **> fav:**")

        if len(name) > 25:
            raise GenericError("**Имя не может превышать 25 символов.**")

        if len(description) > 50:
            raise GenericError("**Описание не может превышать 50 символов.**")

        if len(url) > (max_url_chars:=self.bot.config["USER_FAV_MAX_URL_LENGTH"]):
            raise GenericError(f"**Максимально допустимое количество символов в ссылке: {max_url_chars}**")

        await inter.response.defer(ephemeral=True)

        guild_data = await self.bot.get_data(inter.guild.id, db_name=DBModel.guilds)

        if not guild_data["player_controller"]["channel"] or not self.bot.get_channel(int(guild_data["player_controller"]["channel"])):
            raise GenericError("**На сервере не настроен плеер! Используйте команду /setup**")

        try:
            if name:
                old_data = dict(guild_data["player_controller"]["fav_links"][item])
                del guild_data["player_controller"]["fav_links"][item]
                guild_data["player_controller"]["fav_links"][name] = {
                    'url': url or old_data["url"],
                    "description": description or old_data.get("description")
                }

            elif url:
                guild_data["player_controller"]["fav_links"][item]['url'] = url

            if description:
                guild_data["player_controller"]["fav_links"][item]['description'] = description

        except KeyError:
            raise GenericError(f"**Não há link fixo com o nome:** {item}")

        await self.bot.update_data(inter.guild.id, guild_data, db_name=DBModel.guilds)

        await inter.edit_original_message(embed=disnake.Embed(description="***Фиксированная ссылка успешно отредактирована!**", color=self.bot.get_color(inter.guild.me)))

        await self.process_idle_embed(inter.guild)

    @pin.sub_command(
        name=disnake.Localized("remove", data={disnake.Locale.pt_BR: "remover"}),
        description=f"{desc_prefix}Удалить ссылку из списка фиксированных ссылок сервера."
    )
    async def remove(
            self,
            inter: disnake.AppCmdInter,
            item: str = commands.Param(autocomplete=pin_list, description="Элемент для удаления."),
    ):

        await inter.response.defer(ephemeral=True)

        guild_data = await self.bot.get_data(inter.guild.id, db_name=DBModel.guilds)

        try:
            del guild_data["player_controller"]["fav_links"][item]
        except:
            raise GenericError(f"**Нет ссылок из списка с названием:** {item}")

        await self.bot.update_data(inter.guild.id, guild_data, db_name=DBModel.guilds)

        await inter.edit_original_message(embed=disnake.Embed(description="**Ссылка успешно удалена!**", color=self.bot.get_color(inter.guild.me)))

        await self.process_idle_embed(inter.guild)

    @commands.cooldown(1, 20, commands.BucketType.guild)
    @pin.sub_command(
        name=disnake.Localized("import", data={disnake.Locale.pt_BR: "импорт"}),
        description=f"{desc_prefix}Импорт ссылок из файла. json в список ссылок на сервер."
    )
    async def import_(
            self,
            inter: disnake.ApplicationCommandInteraction,
            file: disnake.Attachment = commands.Param(name="arquivo", description="файл в формате .json")
    ):

        if file.size > 2097152:
            raise GenericError("**Размер файла не может превышать 2Mb!**")

        if not file.filename.endswith(".json"):
            raise GenericError("**Неверный тип файла!**")

        await inter.response.defer(ephemeral=True)

        try:
            data = (await file.read()).decode('utf-8')
            json_data = json.loads(data)
        except Exception as e:
            raise GenericError("**При чтении файла произошла ошибка, проверьте его и повторите команду.**\n"
                               f"```py\n{repr(e)}```")

        for name, data in json_data.items():

            if "> fav:" in name.lower():
                continue

            if len(data['url']) > (max_url_chars := self.bot.config["USER_FAV_MAX_URL_LENGTH"]):
                raise GenericError(f"**Элемент в вашем архиве превышает разрешенное количество символов:{max_url_chars}\nURL:** {data['url']}")

            if len(data['description']) > 50:
                raise GenericError(f"**Элемент в вашем файле превышает допустимое количество символов:{max_url_chars}\nОписание:** {data['description']}")

            if not isinstance(data['url'], str) or not URL_REG.match(data['url']):
                raise GenericError(f"Ваш файл содержит неверную ссылку: ```ldif\n{data['url']}```")

        guild_data = await self.bot.get_data(inter.guild.id, db_name=DBModel.guilds)

        if not guild_data["player_controller"]["channel"] or not self.bot.get_channel(int(guild_data["player_controller"]["channel"])):
            raise GenericError("**На сервере не настроен плеер! Используйте команду /setup**")

        for name in json_data.keys():
            if len(name) > (max_name_chars := 25):
                raise GenericError(f"**Элемент в вашем файле ({name}) превышает разрешенное количество символов:{max_name_chars}**")
            try:
                del guild_data["player_controller"]["fav_links"][name]
            except KeyError:
                continue

        if (json_size:=len(json_data)) > 25:
            raise GenericError(f"Количество элементов в файле превышает максимально допустимое количество (25).")

        if (json_size + (user_favs:=len(guild_data["player_controller"]["fav_links"]))) > 25:
            raise GenericError("В плейлисте/плейлисте на сервере недостаточно места для добавления всех элементов из вашего файла...\n"
                                f"Текущий лимит: 25\n"
                                f"Quantidade de links salvos: {user_favs}\n"
                                f"Тебе доступно: {(json_size + user_favs)-25}")

        guild_data["player_controller"]["fav_links"].update(json_data)

        await self.bot.update_data(inter.guild.id, guild_data, db_name=DBModel.guilds)

        await inter.edit_original_message(
            embed = disnake.Embed(
                color=self.bot.get_color(inter.guild.me),
                description = "**Ссылки успешно импортированы!**\n"
                              "**Они будут появляться, когда плеер не используется или находится в режиме ожидания.**",
            )
        )

        await self.process_idle_embed(inter.guild)

    @commands.cooldown(1, 20, commands.BucketType.guild)
    @pin.sub_command(
        name=disnake.Localized("export", data={disnake.Locale.pt_BR: "Экспорт"}),
        description=f"{desc_prefix}Экспортируйте фиксированные ссылки на музыку/плейлист сервера в файл json."
    )
    async def export(self, inter: disnake.ApplicationCommandInteraction):

        await inter.response.defer(ephemeral=True)

        guild_data = await self.bot.get_data(inter.guild.id, db_name=DBModel.guilds)

        if not guild_data["player_controller"]["fav_links"]:
            raise GenericError(f"**На сервере нет закрепленных песен/плейлистов.\n"
                               f"Вы можете добавить с помощью команды: /{self.pin.name} {self.add.name}**")

        fp = BytesIO(bytes(json.dumps(guild_data["player_controller"]["fav_links"], indent=4), 'utf-8'))

        embed = disnake.Embed(
            description=f"**Фиксированные данные ссылки на серверную песню / плейлист здесь.\n"
                        f"Вы можете импортировать с помощью команды:** `/{self.pin.name} {self.add.name}`",
            color=self.bot.get_color(inter.guild.me))

        await inter.edit_original_message(embed=embed, file=disnake.File(fp=fp, filename="guild_favs.json"))


def setup(bot: BotCore):
    bot.add_cog(PinManager(bot))
