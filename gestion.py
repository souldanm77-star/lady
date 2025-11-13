"""
gestion.py - Lady Glam Manager
Interface Tkinter principale utilisant les modules séparés
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from pathlib import Path
import time
from PIL import Image, ImageTk

# Ajout du chemin du projet pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import des modules de la structure du projet
from modules.database_manager import DatabaseManager
from modules.product_service import ProductService
from modules.products_exporter import ProductsExporter
from modules.ui_helpers import show_info, show_error, show_warning, ask_yes_no

# ============================================================================
# DESIGN SYSTEM - MINIMALISTE MODE CLAIR (inchangé)
# ============================================================================

class MinimalDesign:
    """Design System Minimaliste avec palette claire et épurée"""
    
    COLORS = {
        # Backgrounds épurés
        'bg_primary': '#ffffff',
        'bg_secondary': '#f8f9fa',
        'bg_tertiary': '#f1f3f5',
        'bg_hover': '#e9ecef',
        
        # Accents subtils
        'accent': '#2563eb',      # Bleu professionnel
        'accent_light': '#3b82f6',
        'accent_hover': '#1d4ed8',
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        
        # Texte haute lisibilité
        'text_primary': '#1f2937',
        'text_secondary': '#6b7280',
        'text_muted': '#9ca3af',
        
        # Bordures fines
        'border': '#e5e7eb',
        'border_focus': '#2563eb',
        'border_light': '#f3f4f6',
        
        # Ombres subtiles
        'shadow': '#00000008',
    }
    
    FONTS = {
        'family': 'Inter',
        'family_alt': 'Segoe UI',
        'size_xs': 10,
        'size_sm': 11,
        'size_base': 12,
        'size_lg': 14,
        'size_xl': 16,
        'size_2xl': 20,
        'size_3xl': 28,
    }
    
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 24,
        '2xl': 32,
        '3xl': 48,
    }
    
    RADIUS = {
        'sm': 4,
        'md': 8,
        'lg': 12,
        'xl': 16,
    }

DS = MinimalDesign()

# ============================================================================
# WIDGETS MINIMALISTES (inchangés)
# ============================================================================

class MinimalButton(tk.Canvas):
    """Bouton minimaliste avec hover subtil"""
    
    def __init__(self, parent, text="", command=None, icon="", style="primary", width=120, height=36, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=DS.COLORS['bg_primary'], highlightthickness=0, **kwargs)
        
        self.text = text
        self.icon = icon
        self.command = command
        self.style = style
        self.width = width
        self.height = height
        self.is_hovered = False
        
        # Styles
        self.styles = {
            'primary': {
                'bg': DS.COLORS['accent'],
                'hover': DS.COLORS['accent_hover'],
                'text': '#ffffff'
            },
            'secondary': {
                'bg': DS.COLORS['bg_tertiary'],
                'hover': DS.COLORS['bg_hover'],
                'text': DS.COLORS['text_primary']
            },
            'success': {
                'bg': DS.COLORS['success'],
                'hover': '#059669',
                'text': '#ffffff'
            },
            'danger': {
                'bg': DS.COLORS['danger'],
                'hover': '#dc2626',
                'text': '#ffffff'
            }
        }
        
        self.draw_button()
        self.bind_events()
    
    def draw_button(self):
        self.delete("all")
        style_config = self.styles.get(self.style, self.styles['primary'])
        
        bg_color = style_config['hover'] if self.is_hovered else style_config['bg']
        
        # Rectangle arrondi
        self.create_rectangle(
            0, 0, self.width, self.height,
            fill=bg_color, outline='', width=0
        )
        
        # Texte
        display_text = f"{self.icon} {self.text}" if self.icon else self.text
        self.create_text(
            self.width/2, self.height/2,
            text=display_text,
            fill=style_config['text'],
            font=(DS.FONTS['family_alt'], DS.FONTS['size_sm'], 'normal')
        )
    
    def bind_events(self):
        self.bind('<Enter>', lambda e: self.on_hover(True))
        self.bind('<Leave>', lambda e: self.on_hover(False))
        self.bind('<Button-1>', self.on_click)
        self.config(cursor='hand2')
    
    def on_hover(self, entered):
        self.is_hovered = entered
        self.draw_button()
    
    def on_click(self, e):
        if self.command:
            self.command()

class MinimalEntry(tk.Frame):
    """Entry minimaliste avec label"""
    
    def __init__(self, parent, label="", placeholder="", **kwargs):
        super().__init__(parent, bg=DS.COLORS['bg_primary'])
        
        self.label_text = label
        self.placeholder = placeholder
        
        # Label
        if label:
            tk.Label(self, text=label,
                    bg=DS.COLORS['bg_primary'],
                    fg=DS.COLORS['text_secondary'],
                    font=(DS.FONTS['family_alt'], DS.FONTS['size_xs'])).pack(anchor='w', pady=(0, DS.SPACING['xs']))
        
        # Container avec border
        container = tk.Frame(self, bg=DS.COLORS['border'], height=32)
        container.pack(fill=tk.X)
        
        inner = tk.Frame(container, bg=DS.COLORS['bg_primary'])
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Entry
        self.entry = tk.Entry(inner,
                             bg=DS.COLORS['bg_primary'],
                             fg=DS.COLORS['text_primary'],
                             font=(DS.FONTS['family_alt'], DS.FONTS['size_sm']),
                             relief=tk.FLAT, bd=0,
                             insertbackground=DS.COLORS['accent'])
        self.entry.pack(fill=tk.BOTH, expand=True, padx=DS.SPACING['sm'], pady=DS.SPACING['xs'])
        
        # Placeholder
        if placeholder:
            self.entry.insert(0, placeholder)
            self.entry.config(fg=DS.COLORS['text_muted'])
            self.entry.bind('<FocusIn>', self._clear_placeholder)
            self.entry.bind('<FocusOut>', self._restore_placeholder)
        
        # Focus border
        self.entry.bind('<FocusIn>', lambda e: container.config(bg=DS.COLORS['border_focus']))
        self.entry.bind('<FocusOut>', lambda e: container.config(bg=DS.COLORS['border']))
    
    def _clear_placeholder(self, e):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=DS.COLORS['text_primary'])
    
    def _restore_placeholder(self, e):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=DS.COLORS['text_muted'])
    
    def get(self):
        val = self.entry.get()
        return "" if val == self.placeholder else val
    
    def delete(self, first, last):
        self.entry.delete(first, last)
    
    def insert(self, index, string):
        self.entry.delete(0, tk.END)
        self.entry.insert(index, string)
        self.entry.config(fg=DS.COLORS['text_primary'])

class MinimalCard(tk.Frame):
    """Carte minimaliste avec ombre légère"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=DS.COLORS['bg_primary'], **kwargs)
        
        # Ombre subtile
        self.config(highlightbackground=DS.COLORS['border'], highlightthickness=1)
        
        # Inner padding
        self.inner = tk.Frame(self, bg=DS.COLORS['bg_primary'])
        self.inner.pack(fill=tk.BOTH, expand=True, padx=DS.SPACING['xl'], pady=DS.SPACING['xl'])

class SimpleToast(tk.Toplevel):
    """Toast notification minimaliste"""
    
    def __init__(self, parent, message, type_msg="info", duration=2500):
        super().__init__(parent)
        
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        
        colors = {
            'success': DS.COLORS['success'],
            'error': DS.COLORS['danger'],
            'warning': DS.COLORS['warning'],
            'info': DS.COLORS['accent']
        }
        
        icons = {
            'success': '✓',
            'error': '✕',
            'warning': '⚠',
            'info': 'ℹ'
        }
        
        color = colors.get(type_msg, colors['info'])
        icon = icons.get(type_msg, icons['info'])
        
        # Container
        container = tk.Frame(self, bg=DS.COLORS['bg_primary'],
                           highlightbackground=color, highlightthickness=2)
        container.pack(padx=0, pady=0)
        
        # Content
        content = tk.Frame(container, bg=DS.COLORS['bg_primary'])
        content.pack(padx=DS.SPACING['lg'], pady=DS.SPACING['md'])
        
        tk.Label(content, text=f"{icon}  {message}",
                bg=DS.COLORS['bg_primary'],
                fg=DS.COLORS['text_primary'],
                font=(DS.FONTS['family_alt'], DS.FONTS['size_sm'])).pack()
        
        # Position
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        x = sw - w - 30
        y = 30
        
        self.geometry(f'+{x}+{y}')
        
        # Fade
        self.attributes('-alpha', 0.0)
        self._fade_in()
        self.after(duration, self._fade_out)
    
    def _fade_in(self, alpha=0.0):
        alpha += 0.1
        if alpha < 1.0:
            self.attributes('-alpha', alpha)
            self.after(20, lambda: self._fade_in(alpha))
        else:
            self.attributes('-alpha', 1.0)
    
    def _fade_out(self, alpha=1.0):
        alpha -= 0.1
        if alpha > 0:
            self.attributes('-alpha', alpha)
            self.after(20, lambda: self._fade_out(alpha))
        else:
            self.destroy()

# ============================================================================
# APPLICATION PRINCIPALE MINIMALISTE
# ============================================================================

class MinimalLadyGlamManager:
    """Interface minimaliste mode clair utilisant les modules séparés"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Lady Glam Manager")
        
        # Configuration
        self.root.minsize(1200, 700)
        self.setup_window()
        
        Path("images").mkdir(exist_ok=True)
        
        self.current_product_id = None
        self.selected_image_path = None
        self.current_product_image = None
        
        # Initialisation des services
        self.db = DatabaseManager("products.json")
        self.service = ProductService(self.db)
        self.exporter = ProductsExporter("products.json", "web/js/products.js")
        
        self.configure_styles()
        self.setup_keyboard_shortcuts()
        self.setup_ui()
    
    def setup_window(self):
        # Configuration initiale de la fenêtre
        self.root.configure(bg=DS.COLORS['bg_secondary'])
        
        # Taille minimum pour garantir l'utilisabilité
        self.root.minsize(900, 600)
        
        # Position et taille initiale
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        
        # Taille adaptative : 80% de l'écran
        w = int(sw * 0.8)
        h = int(sh * 0.8)
        x = (sw - w) // 2
        y = (sh - h) // 2
        
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
        # Bind le redimensionnement
        self.root.bind('<Configure>', self.on_window_resize)
    
    def setup_keyboard_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.clear_form())
        self.root.bind('<Control-s>', lambda e: self.save_product())
        self.root.bind('<F5>', lambda e: self.load_products())
        self.root.bind('<Escape>', lambda e: self.clear_form())
    
    def on_window_resize(self, event=None):
        """Gère le redimensionnement de la fenêtre"""
        if event and event.widget == self.root:
            # Obtenir la nouvelle taille
            width = self.root.winfo_width()
            
            # Ajuster la mise en page en fonction de la taille
            self.adjust_layout(width)
    
    def adjust_layout(self, width):
        """Ajuste la mise en page en fonction de la largeur"""
        if not hasattr(self, 'main'):
            return
            
        # Mode compact pour les petits écrans (< 1200px)
        is_compact = width < 1200
        
        if is_compact:
            # Réorganiser en vue verticale
            self.main.grid_columnconfigure(0, weight=1)
            self.main.grid_columnconfigure(1, weight=0)
            self.form_panel.grid(row=0, column=0, sticky='nsew')
            self.list_panel.grid(row=1, column=0, sticky='nsew')
            
            # Ajuster les marges pour le mode compact
            self.main.pack_configure(padx=DS.SPACING['md'], pady=DS.SPACING['md'])
            
            # Ajuster les tailles de police pour les petits écrans
            self.adjust_font_sizes('compact')
        else:
            # Vue normale horizontale
            self.main.grid_columnconfigure(0, weight=2, minsize=450)
            self.main.grid_columnconfigure(1, weight=3, minsize=650)
            self.form_panel.grid(row=0, column=0, sticky='nsew')
            self.list_panel.grid(row=0, column=1, sticky='nsew')
            
            # Ajuster les marges pour le mode normal
            self.main.pack_configure(padx=DS.SPACING['xl'], pady=DS.SPACING['xl'])
            
            # Ajuster les tailles de police pour les grands écrans
            self.adjust_font_sizes('normal')
    
    def adjust_font_sizes(self, mode):
        """Ajuste les tailles de police en fonction du mode"""
        if mode == 'compact':
            # Tailles réduites pour les petits écrans
            font_scale = 0.9
        else:
            # Tailles normales pour les grands écrans
            font_scale = 1.0
        
        # Appliquer les ajustements de police aux éléments principaux
        if hasattr(self, 'stats_label'):
            current_font = self.stats_label.cget('font')
            if isinstance(current_font, str):
                # Extraire la taille de la police
                font_parts = current_font.split()
                if len(font_parts) >= 3:
                    try:
                        size = int(float(font_parts[2]) * font_scale)
                        font_parts[2] = str(size)
                        self.stats_label.config(font=' '.join(font_parts))
                    except:
                        pass
    
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Minimal.Treeview',
                       background=DS.COLORS['bg_primary'],
                       foreground=DS.COLORS['text_primary'],
                       fieldbackground=DS.COLORS['bg_primary'],
                       font=(DS.FONTS['family_alt'], DS.FONTS['size_sm']),
                       rowheight=40,
                       borderwidth=0)
        
        style.configure('Minimal.Treeview.Heading',
                       background=DS.COLORS['bg_secondary'],
                       foreground=DS.COLORS['text_secondary'],
                       font=(DS.FONTS['family_alt'], DS.FONTS['size_sm'], 'bold'),
                       borderwidth=0,
                       relief='flat')
        
        style.map('Minimal.Treeview',
                 background=[('selected', DS.COLORS['accent'])],
                 foreground=[('selected', '#ffffff')])
        
        style.map('Minimal.Treeview.Heading',
                 background=[('active', DS.COLORS['bg_hover'])])
    
    def setup_ui(self):
        # HEADER responsive
        header = tk.Frame(self.root, bg=DS.COLORS['bg_primary'])
        header.pack(fill=tk.X)
        
        # Container du header avec padding adaptatif
        header_content = tk.Frame(header, bg=DS.COLORS['bg_primary'])
        header_content.pack(fill=tk.BOTH, expand=True, pady=DS.SPACING['lg'])
        
        # Contenu du header avec marge adaptative
        inner_header = tk.Frame(header_content, bg=DS.COLORS['bg_primary'])
        inner_header.pack(fill=tk.BOTH, expand=True)
        
        # Logo + Titre (responsive)
        title_frame = tk.Frame(inner_header, bg=DS.COLORS['bg_primary'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Logo qui s'adapte
        logo_label = tk.Label(title_frame, text="💎",
                bg=DS.COLORS['bg_primary'],
                font=(DS.FONTS['family_alt'], DS.FONTS['size_2xl']))
        logo_label.pack(side=tk.LEFT, padx=(0, DS.SPACING['md']))
        
        # Titre qui s'adapte
        title_label = tk.Label(title_frame, text="Lady Glam Manager",
                bg=DS.COLORS['bg_primary'],
                fg=DS.COLORS['text_primary'],
                font=(DS.FONTS['family_alt'], DS.FONTS['size_xl'], 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Stats (responsive)
        self.stats_label = tk.Label(inner_header, text="0 produits",
                                    bg=DS.COLORS['bg_primary'],
                                    fg=DS.COLORS['text_secondary'],
                                    font=(DS.FONTS['family_alt'], DS.FONTS['size_base']))
        self.stats_label.pack(side=tk.RIGHT, pady=DS.SPACING['md'])
        
        # Separator
        tk.Frame(self.root, bg=DS.COLORS['border'], height=1).pack(fill=tk.X)
        
        # MAIN (container principal responsive)
        self.main = tk.Frame(self.root, bg=DS.COLORS['bg_secondary'])
        self.main.pack(fill=tk.BOTH, expand=True, padx=DS.SPACING['xl'], pady=DS.SPACING['xl'])
        
        # Configuration de la grille responsive
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)  # Pour le mode compact
        self.main.grid_columnconfigure(0, weight=2, minsize=450)
        self.main.grid_columnconfigure(1, weight=3, minsize=650)
        
        # PANNEAU GAUCHE - FORMULAIRE
        self.form_panel = MinimalCard(self.main)
        self.setup_form_panel(self.form_panel)
        self.form_panel.grid(row=0, column=0, sticky='nsew', padx=(0, DS.SPACING['lg']))
        
        # PANNEAU DROIT - LISTE
        self.list_panel = MinimalCard(self.main)
        self.setup_list_panel(self.list_panel)
        self.list_panel.grid(row=0, column=1, sticky='nsew')
        
        # Ajuster la mise en page initiale
        self.adjust_layout(self.root.winfo_width())
    
    def setup_form_panel(self, card):
        # Configuration du padding adaptatif
        card.inner.pack(fill=tk.BOTH, expand=True, padx=DS.SPACING['xl'], pady=DS.SPACING['xl'])
        
        # Header
        tk.Label(card.inner, text="Nouveau Produit",
                bg=DS.COLORS['bg_primary'],
                fg=DS.COLORS['text_primary'],
                font=(DS.FONTS['family_alt'], DS.FONTS['size_xl'], 'bold')).pack(anchor='w', pady=(0, DS.SPACING['lg']))
        
        # Formulaire SANS scroll - tout visible
        form = tk.Frame(card.inner, bg=DS.COLORS['bg_primary'])
        form.pack(fill=tk.BOTH, expand=True)
        
        # Grille 2 colonnes pour optimiser l'espace
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        
        row = 0
        
        # Ligne 1: Nom (sur 2 colonnes)
        self.entry_name = MinimalEntry(form, label="Nom du produit", placeholder="Ex: Robe élégante")
        self.entry_name.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0, DS.SPACING['sm']))
        row += 1
        
        # Ligne 2: Catégorie + Prix
        cat_container = tk.Frame(form, bg=DS.COLORS['bg_primary'])
        cat_container.grid(row=row, column=0, sticky='ew', padx=(0, DS.SPACING['xs']))
        
        tk.Label(cat_container, text="Catégorie",
                bg=DS.COLORS['bg_primary'],
                fg=DS.COLORS['text_secondary'],
                font=(DS.FONTS['family_alt'], DS.FONTS['size_xs'])).pack(anchor='w', pady=(0, 2))
        
        cat_border = tk.Frame(cat_container, bg=DS.COLORS['border'])
        cat_border.pack(fill=tk.X)
        
        cat_inner = tk.Frame(cat_border, bg=DS.COLORS['bg_primary'])
        cat_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.combo_category = ttk.Combobox(cat_inner,
                                          values=["Mode & Vêtements", "Accessoires & Lifestyle",
                                                  "Soins Visage", "Soins Corps", "Soins Capillaires", "Parfumerie"],
                                          font=(DS.FONTS['family_alt'], DS.FONTS['size_sm']),
                                          height=8,
                                          state='readonly')
        self.combo_category.pack(fill=tk.X, padx=DS.SPACING['sm'], pady=DS.SPACING['xs'])
        self.combo_category.current(0)
        
        self.entry_price = MinimalEntry(form, label="Prix (FDJ)", placeholder="0.00")
        self.entry_price.grid(row=row, column=1, sticky='ew', padx=(DS.SPACING['xs'], 0))
        row += 1
        
        # Ligne 3: Note + Badge
        rating_cont = tk.Frame(form, bg=DS.COLORS['bg_primary'])
        rating_cont.grid(row=row, column=0, sticky='ew', padx=(0, DS.SPACING['xs']), pady=(DS.SPACING['sm'], 0))
        
        tk.Label(rating_cont, text="Note",
                bg=DS.COLORS['bg_primary'],
                fg=DS.COLORS['text_secondary'],
                font=(DS.FONTS['family_alt'], DS.FONTS['size_xs'])).pack(anchor='w', pady=(0, 2))
        
        rating_border = tk.Frame(rating_cont, bg=DS.COLORS['border'])
        rating_border.pack(fill=tk.X)
        
        rating_inner = tk.Frame(rating_border, bg=DS.COLORS['bg_primary'])
        rating_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.spinbox_rating = tk.Spinbox(rating_inner, from_=1, to=5,
                                        bg=DS.COLORS['bg_primary'],
                                        fg=DS.COLORS['text_primary'],
                                        font=(DS.FONTS['family_alt'], DS.FONTS['size_sm']),
                                        relief=tk.FLAT, bd=0, width=5)
        self.spinbox_rating.pack(padx=DS.SPACING['sm'], pady=DS.SPACING['xs'])
        self.spinbox_rating.delete(0, tk.END)
        self.spinbox_rating.insert(0, "5")
        
        badge_cont = tk.Frame(form, bg=DS.COLORS['bg_primary'])
        badge_cont.grid(row=row, column=1, sticky='ew', padx=(DS.SPACING['xs'], 0), pady=(DS.SPACING['sm'], 0))
        
        tk.Label(badge_cont, text="Badge",
                bg=DS.COLORS['bg_primary'],
                fg=DS.COLORS['text_secondary'],
                font=(DS.FONTS['family_alt'], DS.FONTS['size_xs'])).pack(anchor='w', pady=(0, 2))
        
        badge_border = tk.Frame(badge_cont, bg=DS.COLORS['border'])
        badge_border.pack(fill=tk.X)
        
        badge_inner = tk.Frame(badge_border, bg=DS.COLORS['bg_primary'])
        badge_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.combo_badge = ttk.Combobox(badge_inner,
                                       values=["", "Best-seller", "Nouveau", "Premium", "Bio"],
                                       font=(DS.FONTS['family_alt'], DS.FONTS['size_sm']),
                                       height=6)
        self.combo_badge.pack(fill=tk.X, padx=DS.SPACING['sm'], pady=DS.SPACING['xs'])
        self.combo_badge.current(0)
        row += 1
        
        # Ligne 4: Description (2 colonnes, plus courte)
        desc_cont = tk.Frame(form, bg=DS.COLORS['bg_primary'])
        desc_cont.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(DS.SPACING['sm'], 0))
        
        tk.Label(desc_cont, text="Description",
                bg=DS.COLORS['bg_primary'],
                fg=DS.COLORS['text_secondary'],
                font=(DS.FONTS['family_alt'], DS.FONTS['size_xs'])).pack(anchor='w', pady=(0, 2))
        
        desc_border = tk.Frame(desc_cont, bg=DS.COLORS['border'])
        desc_border.pack(fill=tk.X)
        
        desc_inner = tk.Frame(desc_border, bg=DS.COLORS['bg_primary'])
        desc_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.text_description = tk.Text(desc_inner, height=2,
                                       bg=DS.COLORS['bg_primary'],
                                       fg=DS.COLORS['text_primary'],
                                       font=(DS.FONTS['family_alt'], DS.FONTS['size_sm']),
                                       relief=tk.FLAT, bd=0, wrap=tk.WORD)
        self.text_description.pack(fill=tk.BOTH, expand=True, padx=DS.SPACING['sm'], pady=DS.SPACING['xs'])
        row += 1
        
        # Ligne 5: Image (2 colonnes, compacte)
        img_cont = tk.Frame(form, bg=DS.COLORS['bg_primary'])
        img_cont.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(DS.SPACING['sm'], 0))
        
        tk.Label(img_cont, text="Image du produit",
                bg=DS.COLORS['bg_primary'],
                fg=DS.COLORS['text_secondary'],
                font=(DS.FONTS['family_alt'], DS.FONTS['size_xs'])).pack(anchor='w', pady=(0, 2))
        
        img_border = tk.Frame(img_cont, bg=DS.COLORS['border'])
        img_border.pack(fill=tk.X)
        
        img_inner = tk.Frame(img_border, bg=DS.COLORS['bg_secondary'])
        img_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Image preview et bouton côte à côte
        img_row = tk.Frame(img_inner, bg=DS.COLORS['bg_secondary'])
        img_row.pack(fill=tk.X, padx=DS.SPACING['sm'], pady=DS.SPACING['sm'])
        
        self.preview_frame = tk.Frame(img_row, bg=DS.COLORS['bg_secondary'], width=100, height=100)
        self.preview_frame.pack(side=tk.LEFT, padx=(0, DS.SPACING['sm']))
        self.preview_frame.pack_propagate(False)
        
        self.preview_label = tk.Label(self.preview_frame,
                                     text="📸",
                                     bg=DS.COLORS['bg_secondary'],
                                     fg=DS.COLORS['text_muted'],
                                     font=(DS.FONTS['family_alt'], 28),
                                     cursor='hand2')
        self.preview_label.pack(expand=True)
        self.preview_label.bind('<Button-1>', lambda e: self.select_image())
        
        # Info et bouton à droite
        info_frame = tk.Frame(img_row, bg=DS.COLORS['bg_secondary'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(info_frame, text="Cliquez sur l'icône ou le bouton\npour sélectionner une image",
                bg=DS.COLORS['bg_secondary'],
                fg=DS.COLORS['text_muted'],
                font=(DS.FONTS['family_alt'], DS.FONTS['size_xs']),
                justify=tk.LEFT).pack(anchor='w', pady=(DS.SPACING['xs'], DS.SPACING['sm']))
        
        MinimalButton(info_frame, text="Parcourir", icon="📁",
                     command=self.select_image, style='secondary',
                     width=100, height=28).pack(anchor='w')
        
        # Boutons actions (en bas)
        btn_container = tk.Frame(card.inner, bg=DS.COLORS['bg_primary'])
        btn_container.pack(side=tk.BOTTOM, pady=(DS.SPACING['lg'], 0))
        
        buttons_row = tk.Frame(btn_container, bg=DS.COLORS['bg_primary'])
        buttons_row.pack()
        
        self.btn_add = MinimalButton(buttons_row, text="Ajouter", icon="➕",
                                     command=self.add_product, style='success', width=100, height=32)
        self.btn_add.pack(side=tk.LEFT, padx=DS.SPACING['xs'])
        
        self.btn_update = MinimalButton(buttons_row, text="Modifier", icon="✏️",
                                        command=self.update_product, style='primary', width=100, height=32)
        self.btn_update.pack(side=tk.LEFT, padx=DS.SPACING['xs'])
        
        MinimalButton(buttons_row, text="Nouveau", icon="🔄",
                     command=self.clear_form, style='secondary', width=100, height=32).pack(side=tk.LEFT, padx=DS.SPACING['xs'])
    
    def setup_list_panel(self, card):
        # Configuration du padding adaptatif
        card.inner.pack(fill=tk.BOTH, expand=True, padx=DS.SPACING['xl'], pady=DS.SPACING['xl'])
        
        # Header
        header = tk.Frame(card.inner, bg=DS.COLORS['bg_primary'])
        header.pack(fill=tk.X, pady=(0, DS.SPACING['xl']))
        
        tk.Label(header, text="Catalogue",
                bg=DS.COLORS['bg_primary'],
                fg=DS.COLORS['text_primary'],
                font=(DS.FONTS['family_alt'], DS.FONTS['size_xl'], 'bold')).pack(side=tk.LEFT)
        
        self.product_counter = tk.Label(header, text="(0)",
                                       bg=DS.COLORS['bg_primary'],
                                       fg=DS.COLORS['text_secondary'],
                                       font=(DS.FONTS['family_alt'], DS.FONTS['size_base']))
        self.product_counter.pack(side=tk.LEFT, padx=(DS.SPACING['sm'], 0))
        
        # Toolbar
        toolbar = tk.Frame(card.inner, bg=DS.COLORS['bg_primary'])
        toolbar.pack(fill=tk.X, pady=(0, DS.SPACING['lg']))
        
        toolbar_left = tk.Frame(toolbar, bg=DS.COLORS['bg_primary'])
        toolbar_left.pack(side=tk.LEFT)
        
        MinimalButton(toolbar_left, text="", icon="🔄",
                     command=self.load_products, style='secondary',
                     width=36).pack(side=tk.LEFT, padx=(0, DS.SPACING['xs']))
        
        MinimalButton(toolbar_left, text="Supprimer", icon="🗑️",
                     command=self.delete_product, style='danger',
                     width=120).pack(side=tk.LEFT, padx=DS.SPACING['xs'])
        
        toolbar_right = tk.Frame(toolbar, bg=DS.COLORS['bg_primary'])
        toolbar_right.pack(side=tk.RIGHT)
        
        MinimalButton(toolbar_right, text="Exporter JS", icon="🌐",
                     command=self.export_products_js, style='primary',
                     width=120).pack(side=tk.LEFT, padx=DS.SPACING['xs'])
        
        # Treeview
        tree_container = tk.Frame(card.inner, bg=DS.COLORS['border'])
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        tree_inner = tk.Frame(tree_container, bg=DS.COLORS['bg_primary'])
        tree_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        tree_scroll = ttk.Scrollbar(tree_inner)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(tree_inner,
                                columns=('ID', 'Nom', 'Catégorie', 'Prix', 'Note', 'Badge'),
                                show='headings',
                                yscrollcommand=tree_scroll.set,
                                style='Minimal.Treeview')
        
        tree_scroll.config(command=self.tree.yview)
        
        # Colonnes
        columns_config = {
            'ID': (60, 'center'),
            'Nom': (250, 'w'),
            'Catégorie': (180, 'w'),
            'Prix': (100, 'center'),
            'Note': (80, 'center'),
            'Badge': (120, 'center')
        }
        
        for col, (width, anchor) in columns_config.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.tag_configure('oddrow', background=DS.COLORS['bg_primary'])
        self.tree.tag_configure('evenrow', background=DS.COLORS['bg_secondary'])
        
        self.tree.bind('<<TreeviewSelect>>', self.on_product_select)
    
    # ========================================================================
    # MÉTHODES MÉTIER
    # ========================================================================
    
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                      ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            self.selected_image_path = file_path
            
            try:
                img = Image.open(file_path)
                img.thumbnail((90, 90))
                photo = ImageTk.PhotoImage(img)
                
                self.preview_label.config(image=photo, text="")
                self.preview_label.image = photo
                
                SimpleToast(self.root, f"Image sélectionnée", "success")
            except:
                filename = os.path.basename(file_path)
                self.preview_label.config(text=f"✓\n{filename[:30]}")
                SimpleToast(self.root, "Image sélectionnée", "success")
    
    def validate_form(self, is_update=False):
        name = self.entry_name.get().strip()
        price = self.entry_price.get().strip()
        
        if not name:
            SimpleToast(self.root, "Le nom est obligatoire", "error")
            return False
        
        if not price:
            SimpleToast(self.root, "Le prix est obligatoire", "error")
            return False
        
        try:
            float(price)
        except ValueError:
            SimpleToast(self.root, "Prix invalide", "error")
            return False
        
        if not is_update and not self.selected_image_path:
            SimpleToast(self.root, "Veuillez sélectionner une image", "warning")
            return False
        
        return True
    
    def get_form_data(self):
        image_path = ""
        
        if self.selected_image_path:
            image_ext = os.path.splitext(self.selected_image_path)[1]
            image_name = f"product_{int(time.time())}{image_ext}"
            dest_path = os.path.join("images", image_name)
            
            try:
                import shutil
                shutil.copy2(self.selected_image_path, dest_path)
                image_path = dest_path
                
                if self.current_product_id and self.current_product_image:
                    if os.path.exists(self.current_product_image):
                        try:
                            os.remove(self.current_product_image)
                        except:
                            pass
            except Exception as e:
                SimpleToast(self.root, f"Erreur copie image", "error")
        else:
            if self.current_product_id and self.current_product_image:
                image_path = self.current_product_image
        
        return {
            'name': self.entry_name.get().strip(),
            'category': self.combo_category.get(),
            'price': float(self.entry_price.get().strip()),
            'rating': int(self.spinbox_rating.get()),
            'badge': self.combo_badge.get() if self.combo_badge.get() else None,
            'description': self.text_description.get('1.0', tk.END).strip(),
            'image_path': image_path,
            'icon': '🎁'
        }
    
    def add_product(self):
        if not self.validate_form(is_update=False):
            return
        
        try:
            product_data = self.get_form_data()
            success, message = self.service.add(product_data)
            
            if success:
                SimpleToast(self.root, message, "success")
                self.clear_form()
                self.load_products()
            else:
                SimpleToast(self.root, message, "error")
            
        except Exception as e:
            SimpleToast(self.root, f"Erreur: {e}", "error")
    
    def save_product(self):
        if self.current_product_id:
            self.update_product()
        else:
            self.add_product()
    
    def update_product(self):
        if not self.current_product_id:
            SimpleToast(self.root, "Aucun produit sélectionné", "warning")
            return
        
        if not self.validate_form(is_update=True):
            return
        
        try:
            product_data = self.get_form_data()
            success, message = self.service.update(self.current_product_id, product_data)
            
            if success:
                SimpleToast(self.root, message, "success")
                self.clear_form()
                self.load_products()
            else:
                SimpleToast(self.root, message, "error")
            
        except Exception as e:
            SimpleToast(self.root, f"Erreur: {e}", "error")
    
    def clear_form(self):
        self.current_product_id = None
        self.selected_image_path = None
        self.current_product_image = None
        
        self.entry_name.delete(0, tk.END)
        self.combo_category.current(0)
        self.entry_price.delete(0, tk.END)
        self.spinbox_rating.delete(0, tk.END)
        self.spinbox_rating.insert(0, "5")
        self.combo_badge.set("")
        self.text_description.delete('1.0', tk.END)
        
        self.preview_label.config(image='', text="📸")
        
        if hasattr(self, 'tree'):
            for item in self.tree.selection():
                self.tree.selection_remove(item)
        
        self.entry_name.entry.focus_set()
    
    def load_products(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            products = self.service.get_all()
            
            for i, product in enumerate(products):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                
                self.tree.insert('', 'end', values=(
                    product.get('id', ''),
                    product.get('name', ''),
                    product.get('category', ''),
                    f"{product.get('price', 0):.2f} FDJ",
                    '⭐' * product.get('rating', 0),
                    product.get('badge', '') if product.get('badge') else ""
                ), tags=(tag,))
            
            self.stats_label.config(text=f"{len(products)} produits")
            self.product_counter.config(text=f"({len(products)})")
            
        except Exception as e:
            SimpleToast(self.root, f"Erreur chargement: {e}", "error")
    
    def on_product_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        product_id = item['values'][0]
        
        product = self.service.get_by_id(product_id)
        
        if product:
            self.current_product_id = product.get('id')
            self.current_product_image = product.get('image_path')
            
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, product.get('name', ''))
            
            self.combo_category.set(product.get('category', ''))
            
            self.entry_price.delete(0, tk.END)
            self.entry_price.insert(0, str(product.get('price', '')))
            
            self.spinbox_rating.delete(0, tk.END)
            self.spinbox_rating.insert(0, str(product.get('rating', 5)))
            
            self.combo_badge.set(product.get('badge', '') if product.get('badge') else "")
            
            self.text_description.delete('1.0', tk.END)
            if product.get('description'):
                self.text_description.insert('1.0', product.get('description'))
            
            self.selected_image_path = None
            
            if product.get('image_path') and os.path.exists(product.get('image_path')):
                try:
                    img = Image.open(product.get('image_path'))
                    img.thumbnail((90, 90))
                    photo = ImageTk.PhotoImage(img)
                    
                    self.preview_label.config(image=photo, text="")
                    self.preview_label.image = photo
                except:
                    self.preview_label.config(text=f"📷\n{os.path.basename(product.get('image_path'))[:30]}")
            else:
                self.preview_label.config(text="⚠️\nImage manquante")
    
    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            SimpleToast(self.root, "Aucun produit sélectionné", "warning")
            return
        
        item = self.tree.item(selected[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        result = ask_yes_no("Confirmer", f"Supprimer '{product_name}' ?")
        
        if result:
            try:
                success, message = self.service.delete(product_id)
                if success:
                    SimpleToast(self.root, message, "success")
                    self.clear_form()
                    self.load_products()
                else:
                    SimpleToast(self.root, message, "error")
            except Exception as e:
                SimpleToast(self.root, f"Erreur: {e}", "error")
    
    def export_products_js(self):
        """Exporte les produits vers le fichier JavaScript en utilisant le module ProductsExporter"""
        try:
            success = self.exporter.export_to_js()
            if success:
                SimpleToast(self.root, "Fichier products.js mis à jour avec succès", "success")
            else:
                SimpleToast(self.root, "Erreur lors de l'export", "error")
        except Exception as e:
            SimpleToast(self.root, f"Erreur: {e}", "error")

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

def main():
    root = tk.Tk()
    root.title("Lady Glam Manager")
    
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = MinimalLadyGlamManager(root)
    
    # Charger les produits au démarrage
    root.after(500, app.load_products)
    
    root.mainloop()

if __name__ == "__main__":
    main()