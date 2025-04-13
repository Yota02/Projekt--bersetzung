import os

def open_file(file_path):
    """Ouvre un fichier et retourne son contenu."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_file(file_path, content):
    """Sauvegarde le contenu dans un fichier."""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def file_exists(file_path):
    """Vérifie si un fichier existe."""
    return os.path.exists(file_path)