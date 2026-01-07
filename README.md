# Bot de Seguridad para Discord

Este bot de Discord está diseñado para proporcionar medidas de seguridad y moderación avanzadas para servidores de Discord. Incluye funcionalidades anti-raid, blacklist de palabras, y comandos de moderación.

## Características

### Seguridad
- **Detección de raids**: Monitorea y previene ataques masivos como creación/eliminación de roles, canales, baneos masivos, etc.
- **Blacklist de palabras**: Elimina mensajes con palabras prohibidas y aísla temporalmente a los usuarios.
- **Protección contra .kill**: Comando especial que borra mensajes y aísla a usuarios no administradores indefinidamente.
- **Configuración anti-raid interactiva**: Comando `/configantiraid` que guía al administrador con preguntas para configurar límites.

### Moderación
- Comandos slash para banear, expulsar, silenciar, advertir usuarios.
- Eliminación masiva de mensajes.
- Bloqueo de canales y modo lento.
- Gestión de blacklist.

### Base de Datos
- Usa SQLite para almacenar logs de eventos, acciones y configuraciones por servidor.

## Instalación

### En PC (Windows/Linux/Mac)

1. Clona el repositorio:
   ```
   git clone <url-del-repositorio>
   cd realsecurity
   ```

2. Instala las dependencias:
   ```
   python install.py
   ```

3. Configura el bot:
   - Edita `config.json` con tu token de bot y otras configuraciones.
   - Asegúrate de que el bot tenga permisos de administrador en tu servidor.

4. Ejecuta el bot:
   ```
   python src/bot.py
   ```

### En Termux (Android)

1. Instala Termux desde F-Droid o Google Play Store.

2. Actualiza los paquetes de Termux:
   ```
   pkg update && pkg upgrade
   ```

3. Instala Python y Git:
   ```
   pkg install python git
   ```

4. Clona el repositorio:
   ```
   git clone <url-del-repositorio>
   cd realsecurity
   ```

5. Instala las dependencias:
   ```
   python install.py
   ```

6. Configura el bot:
   - Edita `config.json` con tu token de bot y otras configuraciones.
   - Asegúrate de que el bot tenga permisos de administrador en tu servidor.

7. Ejecuta el bot:
   ```
   python src/bot.py
   ```

## Configuración

Edita `config.json` para personalizar:
- `token`: Tu token de bot de Discord.
- `database`: Ruta a la base de datos SQLite.
- `log_channel_id`: ID del canal para logs (opcional).
- `default_limits`: Límites por defecto para acciones anti-raid.

## Comandos

### Comandos de Moderación
- `/ban <usuario> [razon]`: Banea a un usuario.
- `/kick <usuario> [razon]`: Expulsa a un usuario.
- `/mute <usuario> <tiempo> [razon]`: Silencia a un usuario por minutos.
- `/warn <usuario> <razon]`: Advierte a un usuario.
- `/purge <cantidad>`: Elimina mensajes del canal.
- `/lockdown`: Bloquea el canal.
- `/unlock`: Desbloquea el canal.
- `/slowmode <segundos>`: Establece modo lento.

### Comandos de Configuración
- `/set_limit <accion> <limite>`: Establece límite para una acción.
- `/enable_module <modulo>`: Habilita un módulo.
- `/disable_module <modulo>`: Deshabilita un módulo.
- `/add_blacklist <palabra>`: Añade palabra a blacklist.
- `/remove_blacklist <palabra>`: Elimina palabra de blacklist.
- `/configantiraid`: Configura medidas anti-raid con preguntas interactivas.

### Comandos de Ayuda
- `/help`: Muestra todos los comandos disponibles.

## Funcionalidades Especiales

### Comando .kill
- Si cualquier usuario escribe `.kill`, el mensaje se borra y se registra el evento. Si no es administrador, es aislado indefinidamente hasta que un moderador lo quite. El servidor se bloquea completamente por 10 minutos (ningún bot puede borrar mensajes ni enviar mensajes durante el lockdown).

### Configuración Anti-Raid
El comando `/configantiraid` pregunta interactivamente sobre límites para:
- Creación/eliminación de roles.
- Creación/eliminación de canales.
- Baneos y expulsiones masivas.
- Uniones masivas de miembros.
- Eliminación/envío masivo de mensajes.
- Envío de invitaciones.
- Adición de bots.
- Ventana de tiempo para estas acciones.

## Logs y Eventos

El bot registra eventos como:
- Uniones de miembros.
- Violaciones de blacklist.
- Acciones anti-raid automáticas.
- Uso de comandos especiales.

## Contribución

Si deseas contribuir, por favor crea un issue o pull request en el repositorio.

## Licencia

Este proyecto está bajo la licencia MIT.
