import PyInstaller.__main__
import os

# Chemin vers l'icône de l'Empire
icon_path = os.path.join('src', 'gui', 'assets', 'icon.ico')

PyInstaller.__main__.run([
    'src/main.py',  # Script principal
    '--name=Empire_Translator',  # Nom de l'exécutable
    '--onefile',  # Création d'un seul fichier
    '--noconsole',  # Pas de console en arrière-plan
    '--icon=' + icon_path,  # Icône personnalisée 
    '--add-data=src/gui/assets;gui/assets',  # Inclure les ressources
    '--hidden-import=PIL._tkinter_finder',  # Import caché nécessaire
])