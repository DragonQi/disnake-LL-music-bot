from __future__ import annotations
import traceback
from typing import TYPE_CHECKING, Union
import disnake
from disnake.ext import commands
from .converters import perms_translations
from .errors import NoVoice, NoPlayer, NoSource, NotRequester, NotDJorStaff, DiffVoiceChannel, GenericError, \
    MissingVoicePerms
from .models import LavalinkPlayer
from ..db import DBModel

if TYPE_CHECKING:
    from ..others import CustomContext


def can_send_message(channel: Union[disnake.TextChannel, disnake.VoiceChannel, disnake.Thread]):
    if not channel.permissions_for(channel.guild.me).send_messages:
        raise GenericError(f"**Não tenho permissão de enviar mensagens no canal:** {channel.mention}")

    if not channel.permissions_for(channel.guild.me).embed_links:
        raise GenericError(f"**Não tenho permissão de inserir links no canal: {channel.mention}**")

    return True


async def check_requester_channel(ctx: CustomContext):
    guild_data = await ctx.bot.get_data(ctx.guild.id, db_name=DBModel.guilds)

    if guild_data['player_controller']["channel"] == str(ctx.channel.id):
        raise GenericError("**Não use comandos neste canal!**", self_delete=True, delete_original=15)

    return True


def has_player():
    def predicate(inter):

        try:
            inter.bot.music.players[inter.guild.id]
        except KeyError:
            raise NoPlayer()

        return True

    return commands.check(predicate)


def is_dj():
    async def predicate(inter):

        try:
            if not inter.bot.music.players[inter.guild.id].restrict_mode:
                return True
        except KeyError:
            return True

        if not await has_perm(inter):
            raise NotDJorStaff()

        return True

    return commands.check(predicate)


def can_send_message_check():
    async def predicate(inter):
        can_send_message(inter.channel)
        return True

    return commands.check(predicate)


def is_requester():
    async def predicate(inter):

        try:
            player: LavalinkPlayer = inter.bot.music.players[inter.guild.id]
        except KeyError:
            raise NoPlayer()

        if not player.current:
            raise NoSource()

        if player.current.requester == inter.author.id or not player.restrict_mode:
            return True

        try:
            if await has_perm(inter):
                return True

        except NotDJorStaff:
            pass

        raise NotRequester()

    return commands.check(predicate)


def check_voice():
    def predicate(inter):

        if not inter.author.voice:
            raise NoVoice()

        try:
            if inter.author.voice.channel != inter.guild.me.voice.channel:
                raise DiffVoiceChannel()
        except AttributeError:
            pass

        if not inter.guild.me.voice:

            perms = inter.author.voice.channel.permissions_for(inter.guild.me)

            if not perms.connect or not perms.speak:
                raise MissingVoicePerms(inter.author.voice.channel)

        return True

    return commands.check(predicate)


def has_source():
    def predicate(inter):

        try:
            player = inter.bot.music.players[inter.guild.id]
        except KeyError:
            raise NoPlayer()

        if not player.current:
            raise NoSource()

        return True

    return commands.check(predicate)


def user_cooldown(rate: int, per: int):
    def custom_cooldown(inter: disnake.Interaction):
        # if (await inter.bot.is_owner(inter.author)):
        #   return None  # sem cooldown

        return commands.Cooldown(rate, per)

    return custom_cooldown


#######################################################################


async def has_perm(inter):
    try:
        player: LavalinkPlayer = inter.bot.music.players[inter.guild.id]
    except KeyError:
        return True

    if inter.author.id in player.dj:
        return True

    if inter.author.guild_permissions.manage_channels:
        return True

    user_roles = [r.id for r in inter.author.roles]

    guild_data = await inter.bot.get_data(inter.guild.id, db_name=DBModel.guilds)

    if [r for r in guild_data['djroles'] if int(r) in user_roles]:
        return True

    elif player.restrict_mode:
        raise GenericError(f"**Erro!** Apenas DJ's e membros com a permissão de **{perms_translations['manage_channels']}** "
                           "podem usar este comando/botão com o **modo restrito ativo**...")

    vc = inter.bot.get_channel(player.channel_id)

    if not vc and inter.author.voice:
        player.dj.add(inter.author.id)

    elif inter.bot.intents.members and not [m for m in vc.members if
                                            not m.bot and (m.guild_permissions.manage_channels or m.id in player.dj)]:
        player.dj.add(inter.author.id)
        await inter.channel.send(embed=disnake.Embed(
            description=f"{inter.author.mention} foi adicionado à lista de DJ's por não haver um no canal <#{vc.id}>.",
            color=player.bot.get_color(inter.guild.me)), delete_after=10)
        return True


def can_connect(
        channel: Union[disnake.VoiceChannel, disnake.StageChannel],
        check_other_bots_in_vc: bool = False
):

    perms = channel.permissions_for(channel.guild.me)

    if not perms.connect:
        raise GenericError(f"**Não tenho permissão para conectar no canal {channel.mention}**")

    if not isinstance(channel, disnake.StageChannel):

        if not perms.speak:
            raise GenericError(f"**Não tenho permissão para falar no canal {channel.mention}**")

        if not channel.guild.voice_client and channel.user_limit and (channel.user_limit - len(channel.voice_states)) < 1:
            raise GenericError(f"**O canal {channel.mention} está lotado!**")

    if check_other_bots_in_vc and any(m for m in channel.members if m.bot and m != channel.guild.me):
        raise GenericError(f"**Há outro bot conectado no canal:** <#{channel.id}>")


async def check_deafen(guild: disnake.Guild):

    if guild.me.voice.deaf:
        return True
    elif guild.me.guild_permissions.deafen_members:
        try:
            await guild.me.edit(deafen=True)
            return True
        except:
            traceback.print_exc()
