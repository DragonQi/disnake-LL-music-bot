from __future__ import annotations
import disnake
from disnake.ext import commands
from typing import TYPE_CHECKING
from utils.db import DBModel
from utils.music.converters import URL_REG, fav_list
from utils.music.errors import GenericError
from io import BytesIO
import json

if TYPE_CHECKING:
    from utils.client import BotCore


class FavManager(commands.Cog):

    def __init__(self, bot: BotCore):
        self.bot = bot

    desc_prefix = "⭐ [Избранное] ⭐ | "

    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.slash_command(name=disnake.Localized("fav", data={disnake.Locale.pt_BR: "Избранное"}),)
    async def fav(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @fav.sub_command(
        name=disnake.Localized("add", data={disnake.Locale.pt_BR: "добавить"}),
        description=f"{desc_prefix}Добавьте ссылку (рекомендуется: плейлист) в список избранного."
    )
    async def add(
            self,
            inter: disnake.ApplicationCommandInteraction,
            name: str = commands.Param(name="nome", description="Название избранного"),
            url: str = commands.Param(name="link", description="ссылка на избранное (рекомендуется: плейлиста)"),
    ):

        if len(name) > (max_name_chars:=self.bot.config["USER_FAV_MAX_NAME_LENGTH"]):
            raise GenericError(f"**Максимально допустимое количество символов в имени: {max_name_chars}**")

        if "> fav:" in name.lower():
            raise GenericError("Вы не можете добавить это имя в избранное: **> fav:**")

        if len(url) > (max_url_chars:=self.bot.config["USER_FAV_MAX_URL_LENGTH"]):
            raise GenericError(f"**Максимально допустимое количество символов в ссылке: {max_url_chars}**")

        if not URL_REG.match(url):
            raise GenericError("**Вы не добавили действующую ссылку...**")

        await inter.response.defer(ephemeral=True)

        user_data = await self.bot.get_global_data(inter.author.id, db_name=DBModel.users)

        if len(user_data["fav_links"]) > (max_favs:=self.bot.config["MAX_USER_FAVS"]) and not \
                (await self.bot.is_owner(inter.author)):
            raise GenericError(f"**Вы превысили разрешенное количество страниц избранного ({max_favs}).**")

        try:
            del user_data["fav_links"][name.lower()]
        except KeyError:
            pass

        user_data["fav_links"][name] = url

        await self.bot.update_global_data(inter.author.id, user_data, db_name=DBModel.users)

        await inter.edit_original_message(embed=disnake.Embed(description="**Ссылка успешно сохранена/обновлена ​​в избранное!\n"
                         "Он появится в следующих случаях:** ```\n"
                         "- При использовании команды /play (в автозаполнении поиска)\n"
                         "- Нажав на кнопку запроса музыки в плеере.\n"
                         "- При использовании команды воспроизведения (с префиксом) без имени или ссылки.```",
                         color=self.bot.get_color(inter.guild.me)))

    @fav.sub_command(
        name=disnake.Localized("edit", data={disnake.Locale.pt_BR: "редактировать"}),
        description=f"{desc_prefix}Отредактируйте элемент из списка избранного."
    )
    async def edit(
            self,
            inter: disnake.ApplicationCommandInteraction,
            item: str = commands.Param(autocomplete=fav_list, description="элемент избранного для редактирования."), *,
            name: str = commands.Param(name="novo_nome", default="", description="Новое имя для избранного."),
            url: str = commands.Param(name="novo_link", default="", description="Новая ссылка избранного.")
    ):

        if not name and not url:
            raise GenericError("**Вы не указали ни один из необязательных элементов: novo_nome и novo_link.**")

        if "> fav:" in name.lower():
            raise GenericError("Вы не должны включать это имя в избранное: **> fav:**")

        if len(name) > (max_name_chars:=self.bot.config["USER_FAV_MAX_NAME_LENGTH"]):
            raise GenericError(f"**Максимально допустимое количество символов в имени: {max_name_chars}**")

        if len(url) > (max_url_chars:=self.bot.config["USER_FAV_MAX_URL_LENGTH"]):
            raise GenericError(f"**Максимально допустимое количество символов в ссылке: {max_url_chars}**")

        await inter.response.defer(ephemeral=True)

        user_data = await self.bot.get_global_data(inter.author.id, db_name=DBModel.users)

        try:
            if name:
                new_url = str(user_data["fav_links"][item])
                del user_data["fav_links"][item]
                user_data["fav_links"][name] = url or new_url

            elif url:
                user_data["fav_links"][item] = url

        except KeyError:
            raise GenericError(f"**Нет избранного с именем:** {item}")

        await self.bot.update_global_data(inter.author.id, user_data, db_name=DBModel.users)

        await inter.edit_original_message(embed=disnake.Embed(description="**Избранное успешно изменено!**", color=self.bot.get_color(inter.guild.me)))

    @fav.sub_command(
        name=disnake.Localized("remove", data={disnake.Locale.pt_BR: "remover"}),
        description=f"{desc_prefix}Удалить ссылку из списка избранного."
    )
    async def remove(
            self,
            inter: disnake.ApplicationCommandInteraction,
            item: str = commands.Param(autocomplete=fav_list, description="Избранное удалено."),
    ):

        await inter.response.defer(ephemeral=True)

        user_data = await self.bot.get_global_data(inter.author.id, db_name=DBModel.users)

        try:
            del user_data["fav_links"][item]
        except:
            raise GenericError(f"**Нет избранного с именем:** {item}")

        await self.bot.update_global_data(inter.author.id, user_data, db_name=DBModel.users)

        await inter.edit_original_message(embed=disnake.Embed(description="**Ссылка успешно удалена!**", color=self.bot.get_color(inter.guild.me)))

    @fav.sub_command(
        name=disnake.Localized("clear", data={disnake.Locale.pt_BR: "zerar"}),
        description=f"{desc_prefix}Очистить список избранного")
    async def clear_(self, inter: disnake.ApplicationCommandInteraction):

        await inter.response.defer(ephemeral=True)

        data = await self.bot.get_global_data(inter.author.id, db_name=DBModel.users)

        if not data["fav_links"]:
            raise GenericError("**У вас нет избранных ссылок**")

        data["fav_links"].clear()

        await self.bot.update_global_data(inter.author.id, data, db_name=DBModel.users)

        embed = disnake.Embed(
            description="Ваш список избранного успешно очищен!",
            color=self.bot.get_color(inter.guild.me)
        )

        await inter.edit_original_message(embed=embed)

    @fav.sub_command(
        name=disnake.Localized("list", data={disnake.Locale.pt_BR: "отображение"}),
        description=f"{desc_prefix}Просмотреть список избранного."
    )
    async def list_(
            self, inter: disnake.ApplicationCommandInteraction,
            hidden: bool = commands.Param(
                name="ocultar",
                description="Только вы можете видеть список избранного.",
                default=False)
    ):

        await inter.response.defer(ephemeral=hidden)

        user_data = await self.bot.get_global_data(inter.author.id, db_name=DBModel.users)

        if not user_data["fav_links"]:
            raise GenericError(f"**У вас нет избранных ссылок\n"
                               f"Вы можете добавить с помощью команды: /{self.fav.name} {self.add.name}**")

        embed = disnake.Embed(
            color=self.bot.get_color(inter.guild.me),
            title="Ваши избранные ссылки:",
            description="\n".join(f"{n+1}) [`{f[0]}`]({f[1]})" for n, f in enumerate(user_data["fav_links"].items()))
        )

        embed.set_footer(text="Вы можете использовать их в команде /play")

        await inter.edit_original_message(embed=embed)

    @fav.sub_command(
        name=disnake.Localized("import", data={disnake.Locale.pt_BR: "импорт"}),
        description=f"{desc_prefix}Импортируйте избранное из файла"
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

        for name, url in json_data.items():

            if "> fav:" in name.lower():
                continue

            if len(url) > (max_url_chars := self.bot.config["USER_FAV_MAX_URL_LENGTH"]):
                raise GenericError(f"**Элемент в вашем файле {url} превышает разрешенное количество символов:{max_url_chars}**")

            if not isinstance(url, str) or not URL_REG.match(url):
                raise GenericError(f"Ваш файл содержит неверную ссылку: ```ldif\n{url}```")

        user_data = await self.bot.get_global_data(inter.author.id, db_name=DBModel.users)

        for name in json_data.keys():
            if len(name) > (max_name_chars := self.bot.config["USER_FAV_MAX_NAME_LENGTH"]):
                raise GenericError(f"**Элемент в вашем файле ({name}) превышает разрешенное количество символов:{max_name_chars}**")
            try:
                del user_data["fav_links"][name.lower()]
            except KeyError:
                continue

        if self.bot.config["MAX_USER_FAVS"] > 0 and not (await self.bot.is_owner(inter.author)):

            if (json_size:=len(json_data)) > self.bot.config["MAX_USER_FAVS"]:
                raise GenericError(f"Количество элементов в вашем файле закладок превышает "
                                   f"максимально допустимое количество ({self.bot.config['MAX_USER_FAVS']}).")

            if (json_size + (user_favs:=len(user_data["fav_links"]))) > self.bot.config["MAX_USER_FAVS"]:
                raise GenericError("У вас недостаточно места, чтобы добавить все закладки в файл...\n"
                                   f"Текущий лимит: {self.bot.config['MAX_USER_FAVS']}\n"
                                   f"Количество сохраненных избранных: {user_favs}\n"
                                   f"Тебе доступно: {(json_size + user_favs)-self.bot.config['MAX_USER_FAVS']}")

        user_data["fav_links"].update(json_data)

        await self.bot.update_global_data(inter.author.id, user_data, db_name=DBModel.users)

        await inter.edit_original_message(
            embed = disnake.Embed(
                color=self.bot.get_color(inter.guild.me),
                description = "**Ссылки успешно импортированы!**\n"
                              "**Они появятся, когда вы используете команду /play (в автозаполнении поиска)..**",
            )
        )

    @fav.sub_command(
        name=disnake.Localized("export", data={disnake.Locale.pt_BR: "exportar"}),
        description=f"{desc_prefix}Exportar seus favoritos em um arquivo json."
    )
    async def export(self, inter: disnake.ApplicationCommandInteraction):

        await inter.response.defer(ephemeral=True)

        user_data = await self.bot.get_global_data(inter.author.id, db_name=DBModel.users)

        if not user_data["fav_links"]:
            raise GenericError(f"**Они появляются, когда вы принимаете команду /play (в автозаполнении поиска).\n"
                               f"Вы можете добавить с помощью команды: /{self.fav.name} {self.add.name}**")

        fp = BytesIO(bytes(json.dumps(user_data["fav_links"], indent=4), 'utf-8'))

        embed = disnake.Embed(
            description=f"Ваши любимые здесь.\nВы можете импортировать с помощью команды: `/{self.import_.name}`",
            color=self.bot.get_color(inter.guild.me))

        await inter.edit_original_message(embed=embed, file=disnake.File(fp=fp, filename="favoritos.json"))


def setup(bot: BotCore):
    bot.add_cog(FavManager(bot))
