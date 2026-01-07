import subprocess
import sys

def run_command(command):
    """Ejecuta un comando y devuelve el código de salida, stdout y stderr."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout.strip(), e.stderr.strip()

def check_for_updates():
    """Verifica si hay actualizaciones disponibles en el repositorio."""
    print("Verificando actualizaciones...")
    code, out, err = run_command("git fetch")
    if code != 0:
        print(f"Error al hacer fetch: {err}")
        return False

    code, out, err = run_command("git status -uno")
    if "behind" in out:
        return True
    else:
        print("El repositorio está actualizado.")
        return False

def update_repo():
    """Actualiza el repositorio."""
    print("Actualizando repositorio...")
    code, out, err = run_command("git pull")
    if code == 0:
        print("Repositorio actualizado exitosamente.")
        # Reinstalar dependencias si es necesario
        print("Reinstalando dependencias...")
        run_command("python install.py")
    else:
        print(f"Error al actualizar: {err}")

def main():
    if check_for_updates():
        response = input("Hay actualizaciones disponibles. ¿Quieres actualizar? (y/n): ").strip().lower()
        if response == 'y':
            update_repo()
        else:
            print("Actualización cancelada.")
    else:
        print("No hay actualizaciones disponibles.")

if __name__ == "__main__":
    main()
