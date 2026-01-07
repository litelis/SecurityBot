import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ban', description='Banea a un usuario')
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, usuario: discord.Member, razon: str = None):
        await usuario.ban(reason=razon)
        await interaction.response.send_message(f'{usuario} ha sido baneado. Razón: {razon or "No especificada"}')

    @app_commands.command(name='kick', description='Expulsa a un usuario')
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, usuario: discord.Member, razon: str = None):
        await usuario.kick(reason=razon)
        await interaction.response.send_message(f'{usuario} ha sido expulsado. Razón: {razon or "No especificada"}')

    @app_commands.command(name='mute', description='Silencia a un usuario por minutos')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, usuario: discord.Member, tiempo: int, razon: str = None):
        from datetime import timedelta
        await usuario.timeout(discord.utils.utcnow() + timedelta(minutes=tiempo), reason=razon)
        await interaction.response.send_message(f'{usuario} ha sido silenciado por {tiempo} minutos. Razón: {razon or "No especificada"}')

    @app_commands.command(name='warn', description='Advierte a un usuario')
    @app_commands.checks.has_permissions(administrator=True)
    async def warn(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):
        # Simular warn, enviar DM
        try:
            await usuario.send(f'Has sido advertido por: {razon}')
        except:
            pass
        await interaction.response.send_message(f'{usuario} ha sido advertido. Razón: {razon}')

    @app_commands.command(name='purge', description='Elimina mensajes del canal')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, cantidad: int):
        deleted = await interaction.channel.purge(limit=cantidad)
        await interaction.response.send_message(f'Eliminados {len(deleted)} mensajes.')

    @app_commands.command(name='lockdown', description='Bloquea el canal')
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lockdown(self, interaction: discord.Interaction):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message('Canal bloqueado.')

    @app_commands.command(name='unlock', description='Desbloquea el canal')
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = None
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message('Canal desbloqueado.')

    @app_commands.command(name='slowmode', description='Establece modo lento')
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, segundos: int):
        await interaction.channel.edit(slowmode_delay=segundos)
        await interaction.response.send_message(f'Modo lento establecido a {segundos} segundos.')

    @app_commands.command(name='untimeout', description='Quita el aislamiento a un usuario')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def untimeout(self, interaction: discord.Interaction, usuario: discord.Member):
        await usuario.timeout(None, reason='Aislamiento removido por moderador')
        await interaction.response.send_message(f'Aislamiento removido a {usuario}.')

async def setup(bot):
    await bot.add_cog(Moderation(bot))
