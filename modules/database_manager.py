# modules/database_manager.py

import json
import os
import shutil
from datetime import datetime

class DatabaseManager:
    """
    Gère la base de données JSON des produits.
    S'occupe de la lecture, de l'écriture atomique et des sauvegardes.
    """
    
    def __init__(self, json_file="products.json"):
        self.json_file = json_file
        self.db_backups_dir = "backups/db_backups"
        
        # Crée le dossier de sauvegarde s'il n'existe pas
        os.makedirs(self.db_backups_dir, exist_ok=True)
        
        # Crée le fichier JSON s'il n'existe pas
        if not os.path.exists(self.json_file):
            self.save([])

    def backup_current_version(self):
        """
        Crée une sauvegarde de la version actuelle du fichier JSON.
        Retourne le chemin du fichier de sauvegarde.
        """
        if os.path.exists(self.json_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"products_{timestamp}.json"
            backup_path = os.path.join(self.db_backups_dir, backup_filename)
            shutil.copy2(self.json_file, backup_path)
            print(f"Sauvegarde de la base de données créée : {backup_path}")
            return backup_path
        return None

    def load(self):
        """
        Charge les données depuis le fichier JSON.
        Retourne une liste de produits (vide si erreur ou fichier vide).
        """
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Si le fichier n'existe pas ou est corrompu, on retourne une liste vide
            return []

    def save(self, data):
        """
        Sauvegarde les données dans le fichier JSON de manière atomique.
        Crée une sauvegarde avant d'écrire.
        Retourne True en cas de succès, False en cas d'erreur.
        """
        # 1. Créer une sauvegarde de l'ancienne version
        self.backup_current_version()
        
        # 2. Écriture atomique via un fichier temporaire
        temp_file = f"{self.json_file}.tmp"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 3. Remplacer le fichier original par le fichier temporaire
            os.replace(temp_file, self.json_file)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la base de données : {e}")
            # Nettoyer le fichier temporaire en cas d'erreur
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False
