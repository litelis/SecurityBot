import json
import os
import getpass

def setup_config():
    config_path = 'config.json'

    # Default config structure
    default_config = {
        "token": "",
        "database": "bot.db",
        "log_channel_id": None,
        "default_limits": {
            "max_roles_created": 5,
            "max_roles_deleted": 5,
            "max_channels_created": 5,
            "max_channels_deleted": 5,
            "max_members_banned": 3,
            "max_members_kicked": 3,
            "max_invites_sent": 5,
            "max_bots_added": 2,
            "max_members_joined": 10,
            "max_messages_sent": 100,
            "time_window_minutes": 10
        },
        "guild_configs": {}
    }

    # Load existing config if it exists
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = default_config

    # Ask for token
    token = getpass.getpass("Ingresa el token del bot de Discord: ")
    config["token"] = token

    # Save config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    print("Configuración guardada en config.json")

if __name__ == "__main__":
    setup_config()
