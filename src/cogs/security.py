import discord
from discord import app_commands
from discord.ext import commands
import json
import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Database

config_path = os.path.join(os.path.dirname(__file__), '../../config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(config['database'])
        self.limits = config['default_limits']
        self.blacklist = []
        self.timeouts = {}  # user_id: timeout_until
        self.server_locked_until = None
        self.guild_limits = config.get('guild_configs', {})  # Load from config.json
        # Convert string values to int where necessary
        for guild_id, limits in self.guild_limits.items():
            for key, value in limits.items():
                if isinstance(value, str) and value.isdigit():
                    limits[key] = int(value)

    @commands.Cog.listener()
    async def on_ready(self):
        self.blacklist = await self.db.get_blacklist()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Initialize default limits for new guild
        if str(guild.id) not in self.guild_limits:
            self.guild_limits[str(guild.id)] = self.limits.copy()
            await self.save_config()

    async def get_limits(self, guild_id):
        if guild_id in self.guild_limits:
            return self.guild_limits[guild_id]
        else:
            # Load from db
            limits = self.limits.copy()
            for key in limits.keys():
                value = await self.db.get_config(guild_id, key)
                if value is not None:
                    limits[key] = int(value) if value.isdigit() else value
            self.guild_limits[guild_id] = limits
            return limits

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.db.log_event(member.guild.id, 'member_join', f'{member} se unió')
        await self.db.log_action(member.id, member.guild.id, 'join')
        # Verificar mass join
        limits = await self.get_limits(member.guild.id)
        joins = await self.db.get_actions(member.id, member.guild.id, 'join', limits['time_window_minutes'])
        if joins > limits['max_members_joined']:  # Asumir límite para joins
            await member.ban(reason='Mass join detectado')
            await self.db.log_event(member.guild.id, 'auto_ban', f'{member} baneado por mass join')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        # Check if server is locked
        if self.server_locked_until and discord.utils.utcnow() < self.server_locked_until:
            # During lockdown, prevent all actions
            return
        # Check for .kill
        if message.content.strip() == '.kill':
            await message.delete()
            if not message.author.guild_permissions.administrator:
                # Isolate indefinitely until moderator removes
                await message.author.timeout(None, reason='Uso de .kill sin permisos')
                try:
                    await message.author.send('Has usado .kill sin permisos. Has sido aislado indefinidamente hasta que un moderador te quite el aislamiento.')
                except:
                    pass
                await self.db.log_event(message.guild.id, 'kill_attempt', f'{message.author} intentó usar .kill sin permisos')
            else:
                # Admin uses .kill, just log
                await self.db.log_event(message.guild.id, 'kill_used', f'{message.author} usó .kill')
            # Lock the entire server for 10 minutes regardless of admin status
            await self.lock_server(message.guild, timedelta(minutes=10))
            await self.db.log_event(message.guild.id, 'server_lockdown', f'Servidor bloqueado por 10 minutos debido a uso de .kill por {message.author}')
            return
        # Blacklist check
        for word in self.blacklist:
            if word.lower() in message.content.lower():
                await message.delete()
                timeout_duration = timedelta(minutes=1)
                if message.author.id in self.timeouts:
                    timeout_duration = timedelta(minutes=self.timeouts[message.author.id] * 2)
                await message.author.timeout(discord.utils.utcnow() + timeout_duration, reason='Palabra en blacklist')
                self.timeouts[message.author.id] = timeout_duration.total_seconds() / 60
                try:
                    await message.author.send('Tu mensaje contenía una palabra prohibida. Has sido aislado temporalmente.')
                except:
                    pass
                await self.db.log_event(message.guild.id, 'blacklist_violation', f'{message.author} violó blacklist: {word}')
                return

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        await self.db.log_action(role.guild.owner.id if role.permissions.administrator else 0, role.guild.id, 'role_create')
        limits = await self.get_limits(role.guild.id)
        count = await self.db.get_actions(role.guild.owner.id, role.guild.id, 'role_create', limits['time_window_minutes'])
        if count > limits['max_roles_created']:
            await role.guild.owner.ban(reason='Creación masiva de roles')
            await self.db.log_event(role.guild.id, 'auto_ban', f'{role.guild.owner} baneado por creación masiva de roles')

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await self.db.log_action(role.guild.owner.id, role.guild.id, 'role_delete')
        limits = await self.get_limits(role.guild.id)
        count = await self.db.get_actions(role.guild.owner.id, role.guild.id, 'role_delete', limits['time_window_minutes'])
        if count > limits['max_roles_deleted']:
            await role.guild.owner.ban(reason='Eliminación masiva de roles')
            await self.db.log_event(role.guild.id, 'auto_ban', f'{role.guild.owner} baneado por eliminación masiva de roles')

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await self.db.log_action(channel.guild.owner.id, channel.guild.id, 'channel_create')
        limits = await self.get_limits(channel.guild.id)
        count = await self.db.get_actions(channel.guild.owner.id, channel.guild.id, 'channel_create', limits['time_window_minutes'])
        if count > limits['max_channels_created']:
            await channel.guild.owner.ban(reason='Creación masiva de canales')
            await self.db.log_event(channel.guild.id, 'auto_ban', f'{channel.guild.owner} baneado por creación masiva de canales')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        # Check if server is locked
        if self.server_locked_until and discord.utils.utcnow() < self.server_locked_until:
            # During lockdown, find and ban the bot that deleted the channel
            async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                if entry.target.id == channel.id:
                    deleter = entry.user
                    if deleter.bot:
                        try:
                            await channel.guild.ban(deleter, reason='Intento de eliminación de canal durante lockdown')
                            await self.db.log_event(channel.guild.id, 'auto_ban', f'{deleter} baneado por eliminación de canal durante lockdown')
                        except:
                            pass
                    break
            return
        await self.db.log_action(channel.guild.owner.id, channel.guild.id, 'channel_delete')
        limits = await self.get_limits(channel.guild.id)
        count = await self.db.get_actions(channel.guild.owner.id, channel.guild.id, 'channel_delete', limits['time_window_minutes'])
        if count > limits['max_channels_deleted']:
            await channel.guild.owner.ban(reason='Eliminación masiva de canales')
            await self.db.log_event(channel.guild.id, 'auto_ban', f'{channel.guild.owner} baneado por eliminación masiva de canales')

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.db.log_action(guild.owner.id, guild.id, 'member_ban')
        limits = await self.get_limits(guild.id)
        count = await self.db.get_actions(guild.owner.id, guild.id, 'member_ban', limits['time_window_minutes'])
        if count > limits['max_members_banned']:
            await guild.owner.ban(reason='Baneo masivo de miembros')
            await self.db.log_event(guild.id, 'auto_ban', f'{guild.owner} baneado por baneo masivo')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Asumir kick si no fue ban
        await self.db.log_action(member.guild.owner.id, member.guild.id, 'member_kick')
        limits = await self.get_limits(member.guild.id)
        count = await self.db.get_actions(member.guild.owner.id, member.guild.id, 'member_kick', limits['time_window_minutes'])
        if count > limits['max_members_kicked']:
            await member.guild.owner.ban(reason='Expulsión masiva de miembros')
            await self.db.log_event(member.guild.id, 'auto_ban', f'{member.guild.owner} baneado por expulsión masiva')

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Check if server is locked
        if self.server_locked_until and discord.utils.utcnow() < self.server_locked_until:
            # During lockdown, prevent all deletions
            return
        # Log message deletions for anti-raid
        await self.db.log_action(message.author.id if message.author else 0, message.guild.id, 'message_delete')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        # Log message sends for anti-raid
        await self.db.log_action(message.author.id, message.guild.id, 'message_send')
        # Check limits for message sending
        limits = await self.get_limits(message.guild.id)
        count = await self.db.get_actions(message.author.id, message.guild.id, 'message_send', limits['time_window_minutes'])
        if count > limits.get('max_messages_sent', 100):
            await message.author.timeout(discord.utils.utcnow() + timedelta(minutes=5), reason='Envío masivo de mensajes')
            await self.db.log_event(message.guild.id, 'auto_timeout', f'{message.author} aislado por envío masivo de mensajes')

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.db.log_action(invite.inviter.id, invite.guild.id, 'invite_create')
        limits = await self.get_limits(invite.guild.id)
        count = await self.db.get_actions(invite.inviter.id, invite.guild.id, 'invite_create', limits['time_window_minutes'])
        if count > limits.get('max_invites_sent', 5):
            await invite.inviter.timeout(discord.utils.utcnow() + timedelta(minutes=10), reason='Envío masivo de invitaciones')
            await self.db.log_event(invite.guild.id, 'auto_timeout', f'{invite.inviter} aislado por envío masivo de invitaciones')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Check for bots added
        if member.bot:
            await self.db.log_action(member.guild.owner.id, member.guild.id, 'bot_add')
            limits = await self.get_limits(member.guild.id)
            count = await self.db.get_actions(member.guild.owner.id, member.guild.id, 'bot_add', limits['time_window_minutes'])
            if count > limits.get('max_bots_added', 2):
                await member.guild.owner.ban(reason='Adición masiva de bots')
                await self.db.log_event(member.guild.id, 'auto_ban', f'{member.guild.owner} baneado por adición masiva de bots')

    # Más listeners para invites, bots, etc. (simplificado)

    @app_commands.command(name='add_blacklist', description='Añade una palabra a la blacklist')
    @app_commands.checks.has_permissions(administrator=True)
    async def add_blacklist(self, interaction: discord.Interaction, palabra: str):
        if await self.db.add_blacklist_word(palabra):
            self.blacklist.append(palabra)
            await interaction.response.send_message(f'Palabra "{palabra}" añadida a blacklist')
        else:
            await interaction.response.send_message('Palabra ya en blacklist')

    @app_commands.command(name='remove_blacklist', description='Elimina una palabra de la blacklist')
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_blacklist(self, interaction: discord.Interaction, palabra: str):
        await self.db.remove_blacklist_word(palabra)
        if palabra in self.blacklist:
            self.blacklist.remove(palabra)
        await interaction.response.send_message(f'Palabra "{palabra}" eliminada de blacklist')

    @app_commands.command(name='activateantiraid', description='Activa y configura automáticamente los parámetros anti-raid')
    @app_commands.checks.has_permissions(administrator=True)
    async def activate_antiraid(self, interaction: discord.Interaction):
        # Auto-configure anti-raid limits
        default_limits = {
            'max_members_joined': 5,
            'max_roles_created': 3,
            'max_roles_deleted': 2,
            'max_channels_created': 3,
            'max_channels_deleted': 2,
            'max_members_banned': 3,
            'max_members_kicked': 5,
            'max_messages_sent': 50,
            'max_invites_sent': 3,
            'max_bots_added': 1,
            'time_window_minutes': 10
        }
        # Save to database
        for key, value in default_limits.items():
            await self.db.set_config(interaction.guild.id, key, str(value))
        # Update in memory if loaded
        if interaction.guild.id in self.guild_limits:
            self.guild_limits[interaction.guild.id].update(default_limits)
        await interaction.response.send_message('Anti-raid activado y configurado automáticamente con parámetros estándar.')

    async def lock_server(self, guild, duration):
        self.server_locked_until = discord.utils.utcnow() + duration
        # Lock all text channels
        for channel in guild.text_channels:
            overwrite = channel.overwrites_for(guild.default_role)
            overwrite.send_messages = False
            overwrite.manage_messages = False
            overwrite.manage_channels = False
            await channel.set_permissions(guild.default_role, overwrite=overwrite)
        # Revoke permissions from all bots
        for member in guild.members:
            if member.bot:
                try:
                    await member.edit(roles=[], reason='Lockdown: Revoking permissions from bots')
                except:
                    pass
        # Schedule unlock
        await asyncio.sleep(duration.total_seconds())
        await self.unlock_server(guild)

    async def unlock_server(self, guild):
        self.server_locked_until = None
        # Unlock all text channels
        for channel in guild.text_channels:
            overwrite = channel.overwrites_for(guild.default_role)
            overwrite.send_messages = None
            overwrite.manage_messages = None
            await channel.set_permissions(guild.default_role, overwrite=overwrite)

    async def save_config(self):
        # Load current config
        with open(config_path, 'r') as f:
            current_config = json.load(f)
        # Update guild_configs
        current_config['guild_configs'] = self.guild_limits
        # Save back to file
        with open(config_path, 'w') as f:
            json.dump(current_config, f, indent=4)

async def setup(bot):
    await bot.add_cog(Security(bot))
