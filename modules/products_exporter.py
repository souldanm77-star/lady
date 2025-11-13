# modules/products_exporter.py

import json
import os
import shutil
from datetime import datetime

class ProductsExporter:
    """
    Exporte les produits du fichier JSON vers un fichier JavaScript
    pour être utilisé par le site web.
    """
    
    def __init__(self, json_file="products.json", js_file="web/js/products.js"):
        self.json_file = json_file
        self.js_file = js_file
        self.js_backups_dir = "backups/js_backups"
        
        # Crée le dossier de sauvegarde s'il n'existe pas
        os.makedirs(self.js_backups_dir, exist_ok=True)
        
        # Crée le dossier web/js s'il n'existe pas
        os.makedirs(os.path.dirname(self.js_file), exist_ok=True)

    def backup_current_js_version(self):
        """
        Crée une sauvegarde de la version actuelle du fichier JS.
        Retourne le chemin du fichier de sauvegarde.
        """
        if os.path.exists(self.js_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"products_{timestamp}.js"
            backup_path = os.path.join(self.js_backups_dir, backup_filename)
            shutil.copy2(self.js_file, backup_path)
            print(f"Sauvegarde du fichier JS créée : {backup_path}")
            return backup_path
        return None

    def export_to_js(self):
        """
        Lit le fichier JSON, le convertit en variable JS et l'écrit dans products.js.
        Retourne True en cas de succès, False en cas d'erreur.
        """
        try:
            # 1. Créer une sauvegarde de l'ancien fichier JS
            self.backup_current_js_version()
            
            # 2. Charger les données depuis le fichier JSON
            with open(self.json_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            # 3. Préparer le contenu JavaScript
            # On utilise json.dumps pour garantir une syntaxe JSON/JS valide
            js_content = f"const products = {json.dumps(products, indent=2)};"
            
            # 4. Écriture atomique via un fichier temporaire
            temp_file = f"{self.js_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            # 5. Remplacer le fichier original par le fichier temporaire
            os.replace(temp_file, self.js_file)
            
            print(f"Fichier {self.js_file} mis à jour avec {len(products)} produit(s).")
            return True
            
        except FileNotFoundError:
            print(f"Erreur : Le fichier {self.json_file} n'a pas été trouvé.")
            return False
        except json.JSONDecodeError:
            print(f"Erreur : Le fichier {self.json_file} contient du JSON invalide.")
            return False
        except Exception as e:
            print(f"Erreur inattendue lors de l'export JS : {e}")
            # Nettoyer le fichier temporaire en cas d'erreur
            temp_file = f"{self.js_file}.tmp"
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False
