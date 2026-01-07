import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Database

config_path = os.path.join(os.path.dirname(__file__), '../../config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(config['database'])
        self.limits = config['default_limits']

    @app_commands.command(name='set_limit', description='Establece un límite para una acción')
    @app_commands.checks.has_permissions(administrator=True)
    async def set_limit(self, interaction: discord.Interaction, accion: str, limite: int):
        # Guardar en DB
        await self.db.set_config(interaction.guild.id, f'max_{accion}', str(limite))
        self.limits[f'max_{accion}'] = limite
        await interaction.response.send_message(f'Límite para {accion} establecido a {limite}')

    @app_commands.command(name='enable_module', description='Habilita un módulo')
    @app_commands.checks.has_permissions(administrator=True)
    async def enable_module(self, interaction: discord.Interaction, modulo: str):
        await self.db.set_config(interaction.guild.id, f'module_{modulo}', 'enabled')
        await interaction.response.send_message(f'Módulo {modulo} habilitado')

    @app_commands.command(name='disable_module', description='Deshabilita un módulo')
    @app_commands.checks.has_permissions(administrator=True)
    async def disable_module(self, interaction: discord.Interaction, modulo: str):
        await self.db.set_config(interaction.guild.id, f'module_{modulo}', 'disabled')
        await interaction.response.send_message(f'Módulo {modulo} deshabilitado')

    @app_commands.command(name='configantiraid', description='Configura medidas anti-raid con preguntas interactivas')
    @app_commands.checks.has_permissions(administrator=True)
    async def configantiraid(self, interaction: discord.Interaction):
        await interaction.response.defer()

        questions = [
            ("¿Cuántos roles pueden crearse en 10 minutos antes de activar protección? (actual: {})", 'max_roles_created'),
            ("¿Cuántos roles pueden eliminarse en 10 minutos antes de activar protección? (actual: {})", 'max_roles_deleted'),
            ("¿Cuántos canales pueden crearse en 10 minutos antes de activar protección? (actual: {})", 'max_channels_created'),
            ("¿Cuántos canales pueden eliminarse en 10 minutos antes de activar protección? (actual: {})", 'max_channels_deleted'),
            ("¿Cuántos miembros pueden banearse en 10 minutos antes de activar protección? (actual: {})", 'max_members_banned'),
            ("¿Cuántos miembros pueden expulsarse en 10 minutos antes de activar protección? (actual: {})", 'max_members_kicked'),
            ("¿Cuántas invitaciones pueden enviarse en 10 minutos antes de activar protección? (actual: {})", 'max_invites_sent'),
            ("¿Cuántos bots pueden añadirse en 10 minutos antes de activar protección? (actual: {})", 'max_bots_added'),
            ("¿Cuántos miembros pueden unirse en 10 minutos antes de activar protección? (actual: {})", 'max_members_joined'),
            ("¿Cuántos mensajes pueden enviarse en 10 minutos antes de activar protección? (actual: {})", 'max_messages_sent'),
            ("¿Cuántos minutos debe ser la ventana de tiempo para estas acciones? (actual: {})", 'time_window_minutes')
        ]

        responses = {}
        for question, key in questions:
            current = self.limits.get(key, 'N/A')
            await interaction.followup.send(question.format(current))
            try:
                msg = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user and m.channel == interaction.channel, timeout=60.0)
                responses[key] = int(msg.content.strip())
                await msg.delete()
            except (ValueError, asyncio.TimeoutError):
                await interaction.followup.send("Respuesta inválida o tiempo agotado. Usando valor actual.")
                responses[key] = self.limits.get(key, 0)

        # Save to DB and update limits
        for key, value in responses.items():
            await self.db.set_config(interaction.guild.id, key, str(value))
            self.limits[key] = value

        await interaction.followup.send("Configuración anti-raid actualizada exitosamente!")

async def setup(bot):
    await bot.add_cog(Config(bot))
