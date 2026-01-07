# TODO: Configure Antiraid per Server in config.json

## Steps to Complete

- [x] Modify config.json to include "guild_configs" key as an empty dict
- [x] Update Security.__init__ to load guild_limits from config['guild_configs']
- [x] Add on_guild_join listener to initialize default antiraid limits for new guilds and save to config.json
- [x] Modify get_limits method to load from config.json if not in memory
- [x] Add a save_config method in Security to write guild_limits back to config.json
- [x] Update activate_antiraid command to use save_config instead of db.set_config
- [x] Test the configuration persistence by adding the bot to a server and checking config.json
