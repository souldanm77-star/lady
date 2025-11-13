# modules/product_service.py

class ProductService:
    """
    Logique métier pour la gestion des produits.
    Gère les opérations CRUD avec validation.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.products = self.db.load()
        self._calculate_next_id()

    def _calculate_next_id(self):
        """Calcule le prochain ID disponible."""
        if not self.products:
            self.next_id = 1
            return
        
        max_id = 0
        for product in self.products:
            if isinstance(product.get('id'), int) and product['id'] > max_id:
                max_id = product['id']
        self.next_id = max_id + 1

    def _reload_products(self):
        """Recharge les produits depuis le fichier pour s'assurer d'avoir la dernière version."""
        self.products = self.db.load()

    def get_all(self):
        """Retourne tous les produits."""
        self._reload_products()
        return self.products

    def get_by_id(self, product_id):
        """Retourne un produit par son ID, ou None s'il n'existe pas."""
        self._reload_products()
        for product in self.products:
            if product.get('id') == product_id:
                return product
        return None

    def add(self, product_data):
        """
        Ajoute un nouveau produit.
        product_data: dict avec les informations du produit (sans 'id').
        Retourne un tuple (succès: bool, message: str).
        """
        # Validation des données
        if not product_data.get('name') or not product_data.get('name').strip():
            return False, "Le nom du produit est obligatoire."
        
        try:
            price = float(product_data.get('price', 0))
            if price <= 0:
                return False, "Le prix doit être un nombre supérieur à 0."
        except (ValueError, TypeError):
            return False, "Le prix doit être un nombre valide."

        # Ajout du produit avec un ID auto-incrémenté
        new_product = {
            'id': self.next_id,
            'name': product_data['name'].strip(),
            'price': price,
            'category': product_data.get('category', ''),
            'rating': int(product_data.get('rating', 5)),
            'badge': product_data.get('badge'),
            'description': product_data.get('description', ''),
            'image_path': product_data.get('image_path', ''),
            'icon': product_data.get('icon', '🎁')
        }
        
        self.products.insert(0, new_product) # Ajoute au début de la liste
        self.next_id += 1
        
        # Sauvegarde via le DatabaseManager
        if self.db.save(self.products):
            return True, f"Produit '{new_product['name']}' ajouté avec succès."
        else:
            # En cas d'échec de la sauvegarde, on annule l'ajout en mémoire
            self.products.pop(0)
            self.next_id -= 1
            return False, "Erreur lors de la sauvegarde du produit."

    def update(self, product_id, product_data):
        """
        Met à jour un produit existant.
        product_data: dict avec les nouvelles informations.
        Retourne un tuple (succès: bool, message: str).
        """
        # Validation des données
        if not product_data.get('name') or not product_data.get('name').strip():
            return False, "Le nom du produit est obligatoire."
        
        try:
            price = float(product_data.get('price', 0))
            if price <= 0:
                return False, "Le prix doit être un nombre supérieur à 0."
        except (ValueError, TypeError):
            return False, "Le prix doit être un nombre valide."

        for i, product in enumerate(self.products):
            if product.get('id') == product_id:
                # Mise à jour des champs
                updated_product = {
                    'id': product_id,
                    'name': product_data['name'].strip(),
                    'price': price,
                    'category': product_data.get('category', ''),
                    'rating': int(product_data.get('rating', 5)),
                    'badge': product_data.get('badge'),
                    'description': product_data.get('description', ''),
                    'image_path': product_data.get('image_path', ''),
                    'icon': product_data.get('icon', '🎁')
                }
                self.products[i] = updated_product
                
                # Sauvegarde via le DatabaseManager
                if self.db.save(self.products):
                    return True, f"Produit '{updated_product['name']}' mis à jour."
                else:
                    return False, "Erreur lors de la sauvegarde des modifications."
        
        return False, "Produit non trouvé."

    def delete(self, product_id):
        """
        Supprime un produit.
        Retourne un tuple (succès: bool, message: str).
        """
        product_to_delete = None
        for product in self.products:
            if product.get('id') == product_id:
                product_to_delete = product
                break
        
        if not product_to_delete:
            return False, "Produit non trouvé."
        
        product_name = product_to_delete.get('name', 'Inconnu')
        self.products.remove(product_to_delete)
        
        # Sauvegarde via le DatabaseManager
        if self.db.save(self.products):
            return True, f"Produit '{product_name}' supprimé."
        else:
            # En cas d'échec, on restaure le produit en mémoire
            self.products.append(product_to_delete)
            return False, "Erreur lors de la suppression du produit."
