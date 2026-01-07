import os
import subprocess
import sys

def main():
    is_termux = 'TERMUX_VERSION' in os.environ

    if is_termux:
        print("Detectado Termux. Instalando dependencias directamente...")
        pip_path = sys.executable.replace('python', 'pip') if 'python' in sys.executable else 'pip'
        print("Instalando dependencias...")
        subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
        print("Instalación completada en Termux.")
    else:
        print("Creando entorno virtual...")
        subprocess.check_call([sys.executable, "-m", "venv", ".venv"])

        print("Activando entorno virtual...")
        if os.name == 'nt':  # Windows
            activate_script = os.path.join(".venv", "Scripts", "activate.bat")
            pip_path = os.path.join(".venv", "Scripts", "pip.exe")
        else:  # Unix-like
            activate_script = os.path.join(".venv", "bin", "activate")
            pip_path = os.path.join(".venv", "bin", "pip")

        print("Instalando dependencias...")
        subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])

        print("Instalación completada. Para activar el entorno virtual, ejecuta:")
        if os.name == 'nt':
            print(".venv\\Scripts\\activate")
        else:
            print("source .venv/bin/activate")

if __name__ == "__main__":
    main()
