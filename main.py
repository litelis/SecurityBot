import os
import subprocess
import sys

def run_command(command):
    """Ejecuta un comando en el shell."""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar comando: {e}")
        sys.exit(1)

def main():
    venv_path = ".venv"
    bot_command = "python src/bot.py"

    if os.path.exists(venv_path):
        # Activar entorno virtual
        if os.name == 'nt':  # Windows
            activate_cmd = f"{venv_path}\\Scripts\\activate.bat && {bot_command}"
        else:  # Unix-like (Linux, Mac, Termux)
            activate_cmd = f"source {venv_path}/bin/activate && {bot_command}"
        print("Activando entorno virtual y ejecutando bot...")
        run_command(activate_cmd)
    else:
        # Ejecutar directamente
        print("Ejecutando bot directamente...")
        run_command(bot_command)

if __name__ == "__main__":
    main()
