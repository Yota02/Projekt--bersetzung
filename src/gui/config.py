import os
import sys

def resource_path(relative_path):
    """Obtient le chemin absolu des ressources, fonctionne avec PyInstaller"""
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)