# modules/ui_helpers.py

from tkinter import messagebox

def show_info(title, message):
    """Affiche une boîte de dialogue d'information."""
    messagebox.showinfo(title, message)

def show_warning(title, message):
    """Affiche une boîte d'avertissement."""
    messagebox.showwarning(title, message)

def show_error(title, message):
    """Affiche une boîte d'erreur."""
    messagebox.showerror(title, message)

def ask_yes_no(title, message):
    """
    Pose une question oui/non à l'utilisateur.
    Retourne True si l'utilisateur clique sur 'Oui', False sinon.
    """
    return messagebox.askyesno(title, message)
