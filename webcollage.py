import tkinter as tk
from tkinter import ttk
from styles import Colors, Spacing, Typography
from pathlib import Path
import json
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps, ImageChops
from typing import List, Optional
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    print("Pour activer le drag & drop, installez tkinterdnd2 avec:")
    print("pip install tkinterdnd2")
    DND_FILES = "DND_FILES"
    TkinterDnD = tk.Tk
import math
import os
import platform
import subprocess

class ModernApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Collage")
        self.configure(bg=Colors.SYSTEM_BLACK)
        
        # Configuration de base
        self.setup_window()
        self.setup_styles()
        self.create_ui()
        
        # État
        self.images: List[Path] = []
        self.current_view = "grid"  # ou "preview"
        
        # Définir la couleur de fond par défaut
        self.background_color = tk.StringVar(value=Colors.SYSTEM_BLACK)
    
    def setup_window(self):
        # Configurer la fenêtre en mode light par défaut
        self.geometry("1024x768")
        self.minsize(800, 600)
        
        # Centrer la fenêtre
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1024) // 2
        y = (screen_height - 768) // 2
        self.geometry(f"+{x}+{y}")
    
    def setup_styles(self):
        style = ttk.Style()
        
        # Style de base avec fond sombre
        style.configure("Modern.TFrame",
            background=Colors.BACKGROUND)
            
        # Boutons modernes
        style.configure("Modern.TButton",
            font=Typography.BUTTON,
            padding=(Spacing.M, Spacing.S),
            background=Colors.PRIMARY,
            foreground=Colors.SYSTEM_WHITE)
            
        # Labels avec fond sombre
        style.configure("Title.TLabel",
            font=Typography.TITLE,
            background=Colors.BACKGROUND,
            foreground=Colors.TEXT)
            
        style.configure("Subtitle.TLabel",
            font=Typography.SUBTITLE,
            background=Colors.BACKGROUND,
            foreground=Colors.TEXT_SECONDARY)
        
        # Style pour le texte du thème
        style.configure("Caption.TLabel",
            font=Typography.CAPTION,
            background=Colors.BACKGROUND,
            foreground=Colors.TEXT_SECONDARY,
            justify='center')
        
        # Style pour les scrollbars
        style.configure("TScrollbar",
            background=Colors.BACKGROUND,
            troughcolor=Colors.BACKGROUND,
            bordercolor=Colors.BACKGROUND,
            arrowcolor=Colors.TEXT_SECONDARY)
    
    def create_ui(self):
        # Barre de navigation
        self.nav_bar = NavigationBar(self)
        self.nav_bar.pack(fill='x', pady=(Spacing.M, 0))
        
        # Zone principale
        self.main_container = ttk.Frame(self, style="Modern.TFrame")
        self.main_container.pack(fill='both', expand=True, 
                               padx=Spacing.M, pady=Spacing.M)
        
        # Vue grille par défaut
        self.grid_view = ImageGridView(self.main_container)
        self.grid_view.pack(fill='both', expand=True)
        
        # Bouton de génération en bas
        self.create_bottom_bar()
    
    def create_bottom_bar(self):
        # Barre du bas avec fond blanc et ombre
        bottom_frame = tk.Frame(self, bg=Colors.SURFACE)
        bottom_frame.pack(fill='x', side='bottom')
        
        # Padding pour le contenu
        content_frame = tk.Frame(bottom_frame, bg=Colors.SURFACE, 
                               padx=Spacing.L, pady=Spacing.M)
        content_frame.pack(fill='x')
        
        # Bouton Générer
        generate_button = tk.Button(content_frame,
                                  text="Générer le collage",
                                  font=Typography.BUTTON,
                                  fg=Colors.SYSTEM_WHITE,
                                  bg=Colors.PRIMARY,
                                  activebackground=Colors.SYSTEM_BLUE,
                                  activeforeground=Colors.SYSTEM_WHITE,
                                  relief='flat',
                                  padx=Spacing.XL,
                                  pady=Spacing.M,
                                  command=self.generate_collage)
        generate_button.pack(fill='x')
        
        # Ajouter une ligne de séparation en haut
        separator = tk.Frame(bottom_frame, height=1, bg=Colors.DIVIDER)
        separator.pack(fill='x', side='top')
    
    def generate_collage(self):
        """Générer le collage"""
        if not self.grid_view.images:
            self.show_error_message("Aucune image sélectionnée",
                                  "Ajoutez des images avant de générer le collage")
            return
        
        # Afficher le message de chargement
        loading = self.show_loading_message("Création du collage en cours...")
        try:
            # Créer une nouvelle fenêtre de prévisualisation style iOS
            preview_window = tk.Toplevel(self)
            preview_window.title("Prévisualisation du collage")
            preview_window.configure(bg=Colors.SURFACE)
            
            # Configurer la taille de la fenêtre
            preview_window.geometry("1024x768")
            preview_window.transient(self)
            
            # Barre de navigation en haut
            nav_frame = tk.Frame(preview_window, bg=Colors.SURFACE)
            nav_frame.pack(fill='x', padx=Spacing.M, pady=Spacing.M)
            
            # Titre
            tk.Label(nav_frame, 
                    text="Prévisualisation du collage",
                    font=Typography.TITLE,
                    bg=Colors.SURFACE,
                    fg=Colors.TEXT).pack(side='left')
            
            # Options de taille et couleur
            options_frame = tk.Frame(preview_window, bg=Colors.SURFACE)
            options_frame.pack(fill='x', padx=Spacing.L, pady=Spacing.M)
            
            # Frame pour les dimensions
            dim_frame = tk.Frame(options_frame, bg=Colors.SURFACE)
            dim_frame.pack(side='left')
            
            tk.Label(dim_frame,
                    text="Dimensions:",
                    font=Typography.BODY,
                    bg=Colors.SURFACE,
                    fg=Colors.TEXT).pack(side='left', padx=(0, Spacing.M))
            
            width_var = tk.StringVar(value="2000")
            width_entry = ttk.Entry(dim_frame, textvariable=width_var, width=8)
            width_entry.pack(side='left', padx=Spacing.XS)
            
            tk.Label(dim_frame,
                    text="×",
                    font=Typography.BODY,
                    bg=Colors.SURFACE,
                    fg=Colors.TEXT).pack(side='left', padx=Spacing.XS)
            
            height_var = tk.StringVar(value="2000")
            height_entry = ttk.Entry(dim_frame, textvariable=height_var, width=8)
            height_entry.pack(side='left', padx=Spacing.XS)
            
            tk.Label(dim_frame,
                    text="pixels",
                    font=Typography.BODY,
                    bg=Colors.SURFACE,
                    fg=Colors.TEXT).pack(side='left', padx=Spacing.XS)
            
            # Frame pour les options
            options_right_frame = tk.Frame(options_frame, bg=Colors.SURFACE)
            options_right_frame.pack(side='right')
            
            # Option pour afficher les thèmes
            self.show_themes = tk.BooleanVar(value=False)
            theme_frame = tk.Frame(options_right_frame, bg=Colors.SURFACE)
            theme_frame.pack(side='top', pady=(0, Spacing.M))
            
            theme_check = tk.Checkbutton(theme_frame,
                                        text="Afficher les thèmes",
                                        variable=self.show_themes,
                                        font=Typography.BODY,
                                        bg=Colors.SURFACE,
                                        fg=Colors.TEXT,
                                        selectcolor=Colors.PRIMARY,
                                        activebackground=Colors.SURFACE,
                                        command=lambda: self.create_preview(preview_window))
            theme_check.pack(side='left')
            
            # Frame pour la couleur
            color_frame = tk.Frame(options_right_frame, bg=Colors.SURFACE)
            color_frame.pack(side='top')
            
            tk.Label(color_frame,
                    text="Couleur de fond:",
                    font=Typography.BODY,
                    bg=Colors.SURFACE,
                    fg=Colors.TEXT).pack(side='left', padx=Spacing.M)
            
            # Variable pour stocker la couleur de fond
            self.background_color = tk.StringVar(value='#FFFFFF')
            
            # Bouton de couleur avec aperçu
            color_preview = tk.Frame(color_frame, width=30, height=30, 
                                   bg=self.background_color.get())
            color_preview.pack(side='left', padx=Spacing.XS)
            
            def choose_color():
                from tkinter import colorchooser
                color = colorchooser.askcolor(
                    title="Choisir la couleur de fond",
                    color=self.background_color.get()
                )
                if color[1]:  # color est (RGB, hex)
                    self.background_color.set(color[1])
                    color_preview.configure(bg=color[1])
                    # Mettre à jour la prévisualisation
                    self.create_preview(preview_window)
            
            color_button = tk.Button(color_frame,
                                  text="Choisir",
                                  font=Typography.BODY,
                                  fg=Colors.PRIMARY,
                                  bg=Colors.SURFACE,
                                  activebackground=Colors.SYSTEM_GRAY6,
                                  relief='flat',
                                  padx=Spacing.M,
                                  pady=Spacing.S,
                                  command=choose_color)
            color_button.pack(side='left', padx=Spacing.XS)
            
            # Boutons d'action en bas
            action_frame = tk.Frame(preview_window, bg=Colors.SURFACE)
            action_frame.pack(side='bottom', fill='x', padx=Spacing.L, pady=Spacing.L)
            
            # Bouton Annuler
            tk.Button(action_frame,
                     text="Annuler",
                     font=Typography.BUTTON,
                     fg=Colors.TEXT,
                     bg=Colors.SURFACE,
                     activebackground=Colors.SYSTEM_GRAY6,
                     relief='flat',
                     padx=Spacing.XL,
                     pady=Spacing.M,
                     command=preview_window.destroy).pack(side='left')
            
            # Bouton Sauvegarder
            tk.Button(action_frame,
                     text="Sauvegarder",
                     font=Typography.BUTTON,
                     fg=Colors.SYSTEM_WHITE,
                     bg=Colors.PRIMARY,
                     activebackground=Colors.SYSTEM_BLUE,
                     activeforeground=Colors.SYSTEM_WHITE,
                     relief='flat',
                     padx=Spacing.XL,
                     pady=Spacing.M,
                     command=lambda: self.save_collage(preview_window, 
                                                     int(width_var.get()), 
                                                     int(height_var.get()))).pack(side='right')
            
            # Créer et afficher la prévisualisation
            self.create_preview(preview_window)
        finally:
            loading.destroy()
    
    def create_preview(self, window):
        """Crée la prévisualisation du collage"""
        # Afficher le message de chargement
        loading = self.show_loading_message("Génération de la prévisualisation...")
        try:
            preview_frame = tk.Frame(window, bg=Colors.SURFACE)
            preview_frame.pack(fill='both', expand=True, padx=Spacing.L, pady=Spacing.M)
            
            if self.grid_view.images:
                try:
                    # Vérifier que toutes les images sont valides
                    valid_images = []
                    for path in self.grid_view.images:
                        try:
                            with Image.open(path) as img:
                                if img.mode != 'RGB':
                                    img = img.convert('RGB')
                                valid_images.append(path)
                        except Exception as e:
                            print(f"Erreur lors du chargement de {path}: {e}")
                    
                    if not valid_images:
                        raise Exception("Aucune image valide trouvée")
                    
                    # Créer le collage avec les images valides
                    collage = self.create_collage_image(valid_images, 2000, 2000)
                    
                    if collage is None:
                        raise Exception("Erreur lors de la création du collage")
                    
                    # Redimensionner pour la prévisualisation
                    preview_size = (800, 800)
                    aspect_ratio = collage.width / collage.height
                    if aspect_ratio > 1:
                        preview_size = (800, int(800 / aspect_ratio))
                    else:
                        preview_size = (int(800 * aspect_ratio), 800)
                    
                    preview_collage = collage.copy()
                    preview_collage.thumbnail(preview_size, Image.Resampling.LANCZOS)
                    
                    # Afficher la prévisualisation
                    photo = ImageTk.PhotoImage(preview_collage)
                    label = tk.Label(preview_frame, image=photo, bg=Colors.SURFACE)
                    label.image = photo
                    label.pack(expand=True)
                    
                    # Stocker le collage original pour la sauvegarde
                    self.current_collage = collage
                    
                except Exception as e:
                    error_label = tk.Label(preview_frame,
                                         text=f"Erreur lors de la prévisualisation:\n{str(e)}",
                                         bg=Colors.SURFACE,
                                         fg=Colors.TEXT,
                                         font=Typography.BODY)
                    error_label.pack(expand=True)
                    print(f"Erreur détaillée: {e}")
        finally:
            loading.destroy()
    
    def create_collage_image(self, image_paths, width, height):
        """Crée l'image du collage"""
        # Vérifier si on doit afficher les thèmes
        show_themes = hasattr(self, 'show_themes') and self.show_themes.get()
        
        if show_themes:
            return self._create_grid_collage(image_paths, width, height)
        else:
            return self._create_dense_collage(image_paths, width, height)
    
    def _create_grid_collage(self, image_paths, width, height):
        """Crée un collage en grille avec espaces pour les thèmes"""
        # Afficher le message de chargement
        loading = self.show_loading_message("Création du collage en grille...")
        try:
            # Calculer la disposition
            n_images = len(image_paths)
            cols = math.ceil(math.sqrt(n_images))
            rows = math.ceil(n_images / cols)
            
            # Calculer la taille des vignettes avec padding
            padding = 20  # Espace entre les images
            text_height = 30  # Espace réservé pour le texte
            
            # Ajuster la hauteur des cellules pour inclure l'espace du texte
            cell_width = (width - (cols + 1) * padding) // cols
            cell_height = (height - (rows + 1) * padding) // rows
            
            # Réduire la hauteur de l'image pour laisser de la place au texte
            thumb_width = cell_width
            thumb_height = cell_height - text_height
            
            # Utiliser la couleur de fond sélectionnée
            bg_color = self.background_color.get() if hasattr(self, 'background_color') else '#FFFFFF'
            collage = Image.new('RGB', (width, height), bg_color)
            
            # Créer un objet ImageDraw pour ajouter le texte
            draw = ImageDraw.Draw(collage)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Placer chaque image
            for idx, path in enumerate(image_paths):
                try:
                    with Image.open(path) as img:
                        # Convertir en RGB si nécessaire
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Calculer la position dans la grille
                        row = idx // cols
                        col = idx % cols
                        cell_x = padding + col * (cell_width + padding)
                        cell_y = padding + row * (cell_height + padding)
                        
                        # Calculer les dimensions pour conserver le ratio
                        img_ratio = img.width / img.height
                        thumb_ratio = thumb_width / thumb_height
                        
                        if img_ratio > thumb_ratio:
                            # Image plus large que l'espace
                            new_width = thumb_width
                            new_height = int(thumb_width / img_ratio)
                        else:
                            # Image plus haute que l'espace
                            new_height = thumb_height
                            new_width = int(thumb_height * img_ratio)
                        
                        # Redimensionner l'image
                        img_resized = img.resize((new_width, new_height), 
                                               Image.Resampling.LANCZOS)
                        
                        # Centrer l'image dans son espace
                        paste_x = cell_x + (thumb_width - new_width) // 2
                        paste_y = cell_y + (thumb_height - new_height) // 2
                        
                        # Coller l'image
                        collage.paste(img_resized, (paste_x, paste_y))
                        
                        # Extraire et ajouter le thème
                        theme = self.extract_theme_from_metadata(img)
                        if theme:
                            # Position du texte sous l'image
                            text_y = cell_y + thumb_height + 5
                            # Calculer la largeur du texte pour le centrer
                            text_width = draw.textlength(theme, font=font)
                            text_x = cell_x + (cell_width - text_width) // 2
                            
                            # Choisir la couleur du texte selon le fond
                            text_color = (0, 0, 0) if bg_color.startswith('#FFF') else (255, 255, 255)
                            
                            # Ajouter le texte
                            draw.text((text_x, text_y), theme, 
                                    fill=text_color, font=font)
                
                except Exception as e:
                    print(f"Erreur lors du traitement de {path}: {e}")
            
            return collage
        finally:
            loading.destroy()
    
    def _create_dense_collage(self, image_paths, width, height):
        """Crée un collage dense avec préservation parfaite des ratios et sans espaces blancs"""
        loading = self.show_loading_message("Création du collage dense...")
        try:
            bg_color = self.background_color.get() if hasattr(self, 'background_color') else '#FFFFFF'
            # Créer une image plus grande pour avoir de la marge
            temp_width = int(width * 1.2)
            collage = Image.new('RGB', (temp_width, height), bg_color)
            
            # Charger les images avec leurs ratios originaux
            images = []
            for path in image_paths:
                try:
                    with Image.open(path) as img:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        ratio = img.width / img.height
                        images.append((img.copy(), ratio))
                except Exception as e:
                    print(f"Erreur lors du chargement de {path}: {e}")
            
            if not images:
                return collage

            def compute_layout(photos, target_width):
                """Calcule la disposition optimale pour une ligne"""
                total_ratio = sum(r for _, r in photos)
                if total_ratio == 0:
                    return 0
                return int(target_width / total_ratio)

            def find_best_breakpoint(photos, target_width, min_height, max_height):
                """Trouve le meilleur point de coupure pour une ligne"""
                for i in range(1, len(photos) + 1):
                    row = photos[:i]
                    height = compute_layout(row, target_width)
                    if min_height <= height <= max_height:
                        return i
                return len(photos)

            # Paramètres de disposition
            min_height = int(height * 0.5 / math.sqrt(len(images)))
            max_height = int(height * 2.0 / math.sqrt(len(images)))
            
            # Créer les lignes
            rows = []
            remaining = images[:]
            
            while remaining:
                breakpoint = find_best_breakpoint(remaining, temp_width, min_height, max_height)
                row = remaining[:breakpoint]
                rows.append(row)
                remaining = remaining[breakpoint:]

            # Calculer les hauteurs initiales
            row_heights = []
            for row in rows:
                row_height = compute_layout(row, temp_width)
                row_heights.append(row_height)

            # Ajuster les hauteurs pour remplir exactement la hauteur disponible
            total_height = sum(row_heights)
            if total_height > 0:
                scale_factor = height / total_height
            else:
                scale_factor = 1

            # Placer les images
            y = 0
            for row, row_height in zip(rows, row_heights):
                # Calculer la hauteur finale de la ligne
                final_height = int(row_height * scale_factor)
                
                # Calculer la largeur totale des ratios
                total_ratio = sum(ratio for _, ratio in row)
                
                # Placer les images dans la ligne
                x = 0
                for img, ratio in row:
                    # Calculer la largeur en préservant strictement le ratio
                    img_width = max(1, int(final_height * ratio))
                    img_height = max(1, final_height)
                    
                    # Redimensionner l'image
                    img_resized = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
                    
                    # Coller l'image
                    collage.paste(img_resized, (x, y))
                    x += img_width
                
                y += final_height

            # Trouver les limites réelles du contenu
            def find_content_bounds(img):
                bg = Image.new('RGB', img.size, bg_color)
                diff = ImageChops.difference(img, bg)
                bbox = diff.getbbox()
                return bbox if bbox else (0, 0, img.width, img.height)

            # Recadrer aux dimensions du contenu
            content_bbox = find_content_bounds(collage)
            if content_bbox:
                collage_cropped = collage.crop(content_bbox)
                
                # Redimensionner pour correspondre aux dimensions demandées
                content_ratio = collage_cropped.width / collage_cropped.height
                target_ratio = width / height
                
                if content_ratio > target_ratio:
                    new_height = int(width / content_ratio)
                    final_collage = collage_cropped.resize((width, new_height), Image.Resampling.LANCZOS)
                else:
                    new_width = int(height * content_ratio)
                    final_collage = collage_cropped.resize((new_width, height), Image.Resampling.LANCZOS)
                
                return final_collage
            
            return collage
        finally:
            loading.destroy()
    
    def save_collage(self, window, width, height):
        """Sauvegarder le collage"""
        from tkinter import filedialog
        
        output_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[
                ("JPEG", "*.jpg"),
                ("PNG", "*.png")
            ],
            title="Sauvegarder le collage"
        )
        
        if output_path:
            # Afficher le message de chargement
            loading = self.show_loading_message("Sauvegarde du collage en cours...")
            try:
                # Créer le collage final aux dimensions spécifiées
                final_collage = self.create_collage_image(self.grid_view.images, width, height)
                
                # Sauvegarder l'image
                final_collage.save(output_path, quality=95, optimize=True)
                
                # Fermer la fenêtre de prévisualisation
                window.destroy()
                
                # Ouvrir l'image avec le visualiseur par défaut
                if platform.system() == 'Darwin':       # macOS
                    subprocess.run(['open', output_path])
                elif platform.system() == 'Windows':    # Windows
                    os.startfile(output_path)
                else:                                   # Linux
                    subprocess.run(['xdg-open', output_path])
                
            finally:
                loading.destroy()
    
    def show_error_message(self, title, message):
        # Créer une fenêtre de dialogue style iOS
        dialog = tk.Toplevel(self)
        dialog.title("")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        # Centrer la fenêtre
        dialog.transient(self)
        dialog.grab_set()
        
        # Style iOS
        dialog.configure(bg=Colors.SURFACE)
        
        # Titre
        tk.Label(dialog, text=title,
                font=Typography.TITLE,
                bg=Colors.SURFACE,
                fg=Colors.TEXT).pack(pady=(Spacing.L, Spacing.M))
        
        # Message
        tk.Label(dialog, text=message,
                font=Typography.BODY,
                bg=Colors.SURFACE,
                fg=Colors.TEXT_SECONDARY,
                wraplength=250).pack(pady=Spacing.M)
        
        # Bouton OK
        tk.Button(dialog, text="OK",
                 font=Typography.BUTTON,
                 fg=Colors.PRIMARY,
                 bg=Colors.SURFACE,
                 activebackground=Colors.SYSTEM_GRAY6,
                 activeforeground=Colors.PRIMARY,
                 relief='flat',
                 padx=Spacing.XL,
                 pady=Spacing.M,
                 command=dialog.destroy).pack(pady=Spacing.L)
    
    def show_success_message(self, title, message):
        """Affiche un message de succès style iOS"""
        dialog = tk.Toplevel(self)
        dialog.title("")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=Colors.SURFACE)
        
        # Titre
        tk.Label(dialog, text=title,
                font=Typography.TITLE,
                bg=Colors.SURFACE,
                fg=Colors.PRIMARY).pack(pady=(Spacing.L, Spacing.M))
        
        # Message
        tk.Label(dialog, text=message,
                font=Typography.BODY,
                bg=Colors.SURFACE,
                fg=Colors.TEXT,
                wraplength=250).pack(pady=Spacing.M)
        
        # Bouton OK
        tk.Button(dialog, text="OK",
                 font=Typography.BUTTON,
                 fg=Colors.PRIMARY,
                 bg=Colors.SURFACE,
                 activebackground=Colors.SYSTEM_GRAY6,
                 activeforeground=Colors.PRIMARY,
                 relief='flat',
                 padx=Spacing.XL,
                 pady=Spacing.M,
                 command=dialog.destroy).pack(pady=Spacing.L)
    
    def extract_theme_from_metadata(self, img):
        """Extrait le thème depuis les métadonnées de l'image"""
        try:
            if hasattr(img, 'info') and 'prompt' in img.info:
                metadata_str = img.info['prompt']
                
                try:
                    metadata = json.loads(metadata_str)
                    # Chercher le nœud MegaPromptV2 (202)
                    if "202" in metadata and "inputs" in metadata["202"]:
                        theme = metadata["202"]["inputs"].get("theme")
                        if theme:
                            # Convertir les codes Unicode en caractères
                            theme = theme.encode('utf-8').decode('unicode-escape')
                            # Ne garder que les caractères ASCII alphabétiques, numriques et espaces
                            theme = ''.join(c for c in theme if (c.isascii() and (c.isalpha() or c.isdigit())) or c.isspace())
                            # Supprimer les espaces multiples et les espaces au début/fin
                            theme = ' '.join(theme.split())
                            return theme
                except json.JSONDecodeError as e:
                    print(f"Erreur de parsing JSON: {e}")
                except Exception as e:
                    print(f"Erreur lors du traitement du thème: {e}")
                    
            return None
        except Exception as e:
            print(f"Erreur lors de l'extraction du thème: {e}")
            return None
    
    def show_loading_message(self, message):
        """Affiche un message de chargement flottant"""
        loading_window = tk.Toplevel(self)
        loading_window.overrideredirect(True)  # Pas de décorations de fenêtre
        loading_window.configure(bg=Colors.SURFACE)
        
        # Créer un cadre avec une bordure arrondie
        frame = tk.Frame(loading_window, bg=Colors.SURFACE,
                        padx=Spacing.L, pady=Spacing.M)
        frame.pack()
        
        # Spinner de chargement (caractère unicode qui tourne)
        spinner_label = tk.Label(frame, text="◌",
                               font=('SF Pro Display', 24),
                               fg=Colors.PRIMARY,
                               bg=Colors.SURFACE)
        spinner_label.pack()
        
        # Message
        tk.Label(frame, text=message,
                font=Typography.BODY,
                fg=Colors.TEXT,
                bg=Colors.SURFACE).pack(pady=(Spacing.S, 0))
        
        # Centrer la fenêtre
        loading_window.update_idletasks()
        width = loading_window.winfo_width()
        height = loading_window.winfo_height()
        x = (loading_window.winfo_screenwidth() // 2) - (width // 2)
        y = (loading_window.winfo_screenheight() // 2) - (height // 2)
        loading_window.geometry(f'+{x}+{y}')
        
        # Animation du spinner
        def animate_spinner():
            chars = "◴◷◶◵"
            i = 0
            while loading_window.winfo_exists():
                spinner_label.config(text=chars[i])
                i = (i + 1) % len(chars)
                loading_window.update()
                loading_window.after(100)
        
        # Démarrer l'animation dans un thread
        import threading
        threading.Thread(target=animate_spinner, daemon=True).start()
        
        return loading_window

class NavigationBar(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Modern.TFrame")
        
        # Titre
        ttk.Label(self, text="Collage", 
                 style="Title.TLabel").pack(side='left', padx=Spacing.M)
        
        # Frame pour les boutons à droite
        buttons_frame = tk.Frame(self, bg=Colors.SYSTEM_BLACK)
        buttons_frame.pack(side='right', padx=Spacing.M)
        
        # Bouton +
        add_button = tk.Button(buttons_frame,
                             text="＋",
                             font=('SF Pro Display', 20),
                             fg=Colors.SYSTEM_WHITE,
                             bg=Colors.PRIMARY,
                             activebackground=Colors.SYSTEM_BLUE,
                             activeforeground=Colors.SYSTEM_WHITE,
                             relief='flat',
                             width=3,  # Largeur fixe
                             height=1,  # Hauteur fixe
                             command=self.add_images)
        add_button.pack(side='left', padx=(0, Spacing.M))
        
        # Bouton réinitialiser
        reset_button = tk.Button(buttons_frame,
                               text="Réinitialiser",
                               font=Typography.BUTTON,
                               fg=Colors.SYSTEM_WHITE,
                               bg=Colors.SYSTEM_GRAY,
                               activebackground=Colors.SYSTEM_GRAY2,
                               activeforeground=Colors.SYSTEM_WHITE,
                               relief='flat',
                               width=10,  # Largeur fixe
                               height=1,  # Hauteur fixe
                               command=self.reset_selection)
        reset_button.pack(side='left')
    
    def reset_selection(self):
        # Réinitialiser la vue grille
        self.master.grid_view.reset()
    
    def add_images(self):
        from tkinter import filedialog
        files = filedialog.askopenfilenames(
            title="Sélectionner des images",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.gif"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if files:
            self.master.grid_view.add_images(files)

class ImageGridView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Modern.TFrame")
        self.images = []
        self.thumbnails = []
        self.setup_grid()
        self.setup_drop_zone()
    
    def setup_grid(self):
        # Créer un canvas avec scrollbar pour le défilement
        self.canvas = tk.Canvas(self, 
                              bg=Colors.BACKGROUND,
                              highlightthickness=0,
                              bd=0)  # Supprimer toutes les bordures
        
        self.scrollbar = ttk.Scrollbar(self, 
                                     orient="vertical",
                                     style="TScrollbar",
                                     command=self.canvas.yview)
        
        # Conteneur pour la grille d'images
        self.grid_container = ttk.Frame(self.canvas, style="Modern.TFrame")
        
        # Configurer le canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Placer les widgets
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Créer la fenêtre du canvas
        self.canvas_frame = self.canvas.create_window(
            (0, 0),
            window=self.grid_container,
            anchor="nw",
            width=self.canvas.winfo_width()
        )
        
        # Zone de drop avec message
        self.drop_label = ttk.Label(self,
            text="Glissez vos images ici ou cliquez sur ＋",
            style="Subtitle.TLabel")
        self.drop_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Configurer les événements
        self.grid_container.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Configurer le scroll avec la molette de la souris
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
    
    def on_frame_configure(self, event=None):
        """Mettre à jour la zone de défilement"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Ajuster la largeur du frame intérieur au canvas"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def on_mousewheel(self, event):
        """Gérer le défilement avec la molette de la souris"""
        if self.images:  # Scroll seulement s'il y a des images
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_drop_zone(self):
        # Configurer le drag & drop
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Configurer les événements de survol
        self.dnd_bind('<<DragEnter>>', self.handle_drag_enter)
        self.dnd_bind('<<DragLeave>>', self.handle_drag_leave)
    
    def handle_drop(self, event):
        """Gérer le drop des fichiers"""
        files = self.tk.splitlist(event.data)
        self.add_images(files)
        self.drop_label.configure(
            background=Colors.BACKGROUND,
            foreground=Colors.TEXT_SECONDARY)
    
    def handle_drag_enter(self, event):
        """Effet visuel quand on survole la zone de drop"""
        self.drop_label.configure(
            background=Colors.PRIMARY,
            foreground=Colors.SYSTEM_WHITE)
    
    def handle_drag_leave(self, event):
        """Retour à normal quand on quitte la zone"""
        self.drop_label.configure(
            background=Colors.BACKGROUND,
            foreground=Colors.TEXT_SECONDARY)
    
    def add_images(self, file_paths):
        """Ajouter des images à la grille en préservant strictement les ratios"""
        # Afficher le message de chargement
        app = self.winfo_toplevel()
        loading = app.show_loading_message("Chargement des images en cours...")
        
        try:
            valid_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
            
            for path in file_paths:
                file_path = Path(path)
                if file_path.suffix.lower() in valid_extensions:
                    try:
                        with Image.open(path) as img:
                            # Extraire le thème
                            theme = self.master.master.extract_theme_from_metadata(img)
                            
                            # Créer un conteneur principal avec padding fixe
                            container = ttk.Frame(self.grid_container, style="Modern.TFrame")
                            
                            # Calculer les dimensions en préservant strictement le ratio
                            target_area = 150 * 150  # Surface cible
                            ratio = img.width / img.height
                            
                            # Calculer les dimensions pour maintenir le ratio exact
                            if ratio > 1:  # Image paysage
                                thumb_width = min(200, int(math.sqrt(target_area * ratio)))
                                thumb_height = int(thumb_width / ratio)
                            else:  # Image portrait
                                thumb_height = min(200, int(math.sqrt(target_area / ratio)))
                                thumb_width = int(thumb_height * ratio)
                            
                            # Créer la miniature
                            img_thumb = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(img_thumb)
                            
                            # Image dans un cadre pour centrage
                            img_frame = ttk.Frame(container, style="Modern.TFrame")
                            img_frame.pack(expand=True, fill='both')
                            
                            label = ttk.Label(img_frame, image=photo, style="Modern.TLabel")
                            label.image = photo  # Garder une référence
                            label.pack(expand=True, padx=Spacing.XS, pady=Spacing.XS)
                            
                            # Thème
                            if theme:
                                theme_label = ttk.Label(container, 
                                                      text=theme,
                                                      style="Caption.TLabel",
                                                      wraplength=max(thumb_width, 100))
                                theme_label.pack(pady=(0, Spacing.XS))
                            
                            # Ajouter à la grille avec espacement uniforme
                            row = len(self.images) // 4
                            col = len(self.images) % 4
                            container.grid(row=row, column=col, 
                                         padx=Spacing.M, pady=Spacing.M,
                                         sticky='nsew')
                            
                            # Configurer l'expansion de la grille
                            self.grid_container.grid_columnconfigure(col, weight=1)
                            self.grid_container.grid_rowconfigure(row, weight=1)
                            
                            self.images.append(path)
                            self.thumbnails.append(photo)
                            
                            # Cacher le message si des images sont présentes
                            if self.images:
                                self.drop_label.place_forget()
                            
                            # Mettre à jour la zone de défilement
                            self.on_frame_configure()
                
                    except Exception as e:
                        print(f"Erreur lors du chargement de {path}: {e}")
        
        finally:
            loading.destroy()
    
    def reset(self):
        """Réinitialiser la grille d'images"""
        # Nettoyer la grille
        for widget in self.grid_container.winfo_children():
            widget.destroy()
        
        # Réinitialiser les listes
        self.images.clear()
        self.thumbnails.clear()
        
        # Réafficher le message de drop
        self.drop_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Mettre à jour la zone de défilement
        self.on_frame_configure()

class ActionSheet(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=Colors.SURFACE)
        
        # Options de collage
        self.setup_options()
        
        # Bouton de création
        ttk.Button(self, text="Créer le collage",
                  style="Modern.TButton",
                  command=self.create_collage).pack(
                      fill='x', padx=Spacing.M, pady=Spacing.M)
    
    def setup_options(self):
        # TODO: Ajouter les options (taille, espacement, etc.)
        pass
    
    def create_collage(self):
        # TODO: Implémenter la création du collage
        pass

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop() 