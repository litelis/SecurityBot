import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='help', description='Muestra todos los comandos disponibles')
    @app_commands.checks.has_permissions(administrator=True)
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title='Comandos del Bot de Seguridad', description='Lista de comandos disponibles (solo para administradores)', color=0x00ff00)
        embed.add_field(name='/ban <usuario> [razon]', value='Banea a un usuario', inline=False)
        embed.add_field(name='/kick <usuario> [razon]', value='Expulsa a un usuario', inline=False)
        embed.add_field(name='/mute <usuario> <tiempo> [razon]', value='Silencia a un usuario por minutos', inline=False)
        embed.add_field(name='/warn <usuario> <razon>', value='Advierte a un usuario', inline=False)
        embed.add_field(name='/purge <cantidad>', value='Elimina mensajes del canal', inline=False)
        embed.add_field(name='/lockdown', value='Bloquea el canal', inline=False)
        embed.add_field(name='/slowmode <segundos>', value='Establece modo lento', inline=False)
        embed.add_field(name='/set_limit <accion> <limite>', value='Establece límite para una acción', inline=False)
        embed.add_field(name='/enable_module <modulo>', value='Habilita un módulo', inline=False)
        embed.add_field(name='/disable_module <modulo>', value='Deshabilita un módulo', inline=False)
        embed.add_field(name='/add_blacklist <palabra>', value='Añade palabra a blacklist', inline=False)
        embed.add_field(name='/remove_blacklist <palabra>', value='Elimina palabra de blacklist', inline=False)
        embed.add_field(name='/configantiraid', value='Configura medidas anti-raid', inline=False)
        embed.add_field(name='/help', value='Muestra esta ayuda', inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
