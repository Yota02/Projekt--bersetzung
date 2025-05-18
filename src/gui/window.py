from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from .config import resource_path

# Dictionnaire des langues de l'Empire
LANGUAGES = {
    'German': 'de',
    'Japanese': 'ja',
    'French': 'fr',
    'English': 'en',
    'Russian': 'ru',
    'Italian': 'it',
}

class TranslatorWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Projekt Übersetzung")
        self.root.geometry("800x700")
        self.root.configure(bg='#2B2D32')
        
        icon_path = resource_path(os.path.join("src", "gui", "assets", "icon.ico"))
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"Erreur lors du chargement de l'icône : {e}")
        else:
            print(f"Chemin de l'icône introuvable : {icon_path}")
        
        
        # Configuration du style impérial
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Couleurs de l'Empire
        self.configure_imperial_style()
        
        # Variables
        self.input_files = []  # Liste de fichiers au lieu d'un seul
        self.output_directory = tk.StringVar()
        self.target_lang = tk.StringVar(value='French')
        
        # Charger les ressources
        self.load_resources()
        
        self._create_widgets()
        
    def configure_imperial_style(self):
        # Style principal de l'Empire
        self.style.configure('Empire.TFrame', 
                           background='#2B2D32',
                           relief='solid',
                           borderwidth=2)
        
        self.style.configure('Empire.TLabel',
                           background='#2B2D32',
                           foreground='#D4B886',
                           font=('Times New Roman', 10))
        
        self.style.configure('Empire.TButton', 
                           background='#8B0000',
                           foreground='#D4B886',
                           font=('Times New Roman', 10, 'bold'),
                           padding=10,
                           relief='raised')
        
        self.style.configure('Empire.Horizontal.TProgressbar',
                           background='#8B0000',
                           troughcolor='#1A1B1E')
                           
        self.style.configure('Empire.TEntry',
                           fieldbackground='#1A1B1E',
                           foreground='#D4B886')

    
    def load_resources(self):
        self.imperial_seal = None
        try:
            img_path = resource_path(os.path.join("gui", "assets", "imperial_seal.png"))
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((80, 80))
                self.imperial_seal = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Erreur de chargement de l'image: {e}")

    def _create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20", style='Empire.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # En-tête avec sceau impérial
        header_frame = ttk.Frame(main_frame, style='Empire.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))

        if self.imperial_seal:
            seal_label = ttk.Label(header_frame, image=self.imperial_seal)
            seal_label.pack(side=tk.LEFT, padx=10)

        title_label = ttk.Label(header_frame,
                              text="BUREAU IMPÉRIAL DE TRADUCTION\nSECTION 203",
                              font=('Times New Roman', 20, 'bold'),
                              foreground='#D4B886',
                              background='#2B2D32',
                              justify='center')
        title_label.pack(side=tk.RIGHT, expand=True, pady=10, padx=20)

        # Cadre des documents
        doc_frame = ttk.Frame(main_frame, style='Empire.TFrame')
        doc_frame.pack(fill=tk.X, pady=10)

        # Section documents source (multiple)
        source_frame = ttk.Frame(doc_frame, style='Empire.TFrame')
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(source_frame, text="DOCUMENTS SOURCE:", style='Empire.TLabel').pack(side=tk.LEFT)
        
        self.files_display = tk.Text(source_frame, height=3, width=50, bg='#1A1B1E', fg='#D4B886')
        self.files_display.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.files_display.insert(tk.END, "Aucun fichier sélectionné")
        self.files_display.config(state=tk.DISABLED)
        
        ttk.Button(source_frame, text="SÉLECTIONNER", command=self._browse_input_multiple, 
                   style='Empire.TButton').pack(side=tk.RIGHT)

        # Section dossier de sortie
        output_frame = ttk.Frame(doc_frame, style='Empire.TFrame')
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="DOSSIER DE DESTINATION:", style='Empire.TLabel').pack(side=tk.LEFT)
        
        ttk.Entry(output_frame, textvariable=self.output_directory, width=60,
                 style='Empire.TEntry').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                 
        ttk.Button(output_frame, text="PARCOURIR", command=self._browse_output_directory,
                  style='Empire.TButton').pack(side=tk.RIGHT)

        # Section langue
        lang_frame = ttk.Frame(main_frame, style='Empire.TFrame')
        lang_frame.pack(fill=tk.X, pady=10)

        ttk.Label(lang_frame, text="LANGUE CIBLE:", style='Empire.TLabel').pack(side=tk.LEFT)
        
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.target_lang,
                                values=list(LANGUAGES.keys()), width=30, state='readonly')
        lang_combo.pack(side=tk.LEFT, padx=5)

        # File d'attente
        queue_frame = ttk.Frame(main_frame, style='Empire.TFrame')
        queue_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        queue_header = ttk.Frame(queue_frame, style='Empire.TFrame')
        queue_header.pack(fill=tk.X)
        
        ttk.Label(queue_header, text="FILE DE TRADUCTION:", style='Empire.TLabel').pack(side=tk.LEFT)
        
        self.queue_status = ttk.Label(queue_header, text="Statut: 0/0 fichiers", style='Empire.TLabel')
        self.queue_status.pack(side=tk.RIGHT)
        
        # Affichage de la file d'attente
        queue_container = ttk.Frame(queue_frame, style='Empire.TFrame')
        queue_container.pack(fill=tk.BOTH, expand=True)
        
        self.queue_display = tk.Text(queue_container, height=6, width=70, bg='#1A1B1E', fg='#D4B886')
        self.queue_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        queue_scroll = ttk.Scrollbar(queue_container, command=self.queue_display.yview)
        queue_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.queue_display.config(yscrollcommand=queue_scroll.set)

        # Barre de progression
        progress_frame = ttk.Frame(main_frame, style='Empire.TFrame')
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress = ttk.Progressbar(progress_frame, length=600, mode='determinate',
                                      style='Empire.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X)

        # Bouton d'exécution
        button_frame = ttk.Frame(main_frame, style='Empire.TFrame')
        button_frame.pack(fill=tk.X, pady=10)
        
        execute_button = ttk.Button(button_frame, text="EXÉCUTER LA TRADUCTION",
                                  command=self.start_translation, style='Empire.TButton')
        execute_button.pack()

        # Zone de rapport
        log_frame = ttk.Frame(main_frame, style='Empire.TFrame')
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, height=8, width=70, bg='#1A1B1E', fg='#D4B886',
                              font=('Courier New', 10))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def _browse_input_multiple(self):
        filenames = filedialog.askopenfilenames(
            title="SÉLECTION DES DOCUMENTS SOURCE",
            filetypes=[("Documents PDF", "*.pdf")]
        )
        if filenames:
            self.input_files = list(filenames)
            self.files_display.config(state=tk.NORMAL)
            self.files_display.delete(1.0, tk.END)
            for filename in self.input_files:
                self.files_display.insert(tk.END, f"{os.path.basename(filename)}\n")
            self.files_display.config(state=tk.DISABLED)
            
            # Définir le dossier de sortie par défaut (dossier du premier fichier)
            if not self.output_directory.get():
                self.output_directory.set(os.path.dirname(self.input_files[0]))

    def _browse_output_directory(self):
        directory = filedialog.askdirectory(
            title="SÉLECTION DU DOSSIER DE DESTINATION"
        )
        if directory:
            self.output_directory.set(directory)

    def add_to_queue_display(self, input_file, output_file, lang):
        self.queue_display.config(state=tk.NORMAL)
        file_id = f"file_{len(self.input_files)}"
        self.queue_display.insert(tk.END, f"[EN ATTENTE] {os.path.basename(input_file)} -> {os.path.basename(output_file)}\n")
        self.queue_display.tag_add(file_id, f"{float(self.queue_display.index('end'))-1.0}", f"{self.queue_display.index('end')}")
        self.queue_display.config(state=tk.DISABLED)

    def mark_file_completed(self, input_file):
        self.queue_display.config(state=tk.NORMAL)
        content = self.queue_display.get(1.0, tk.END)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if os.path.basename(input_file) in line:
                lines[i] = line.replace('[EN ATTENTE]', '[TERMINÉ]')
                break
        
        self.queue_display.delete(1.0, tk.END)
        self.queue_display.insert(tk.END, '\n'.join(lines))
        self.queue_display.config(state=tk.DISABLED)
    
    def update_queue_status(self, current, total):
        if total > 0:
            status_text = f"Statut: {current}/{total} fichiers"
        else:
            status_text = "Statut: 0/0 fichiers"
        self.queue_status.config(text=status_text)

    def log(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_text.insert(tk.END, f"{timestamp} {message}\n")
        self.log_text.see(tk.END)

    def start_translation(self):
        if not self.input_files:
            messagebox.showerror(
                "ERREUR DE PROCÉDURE",
                "VEUILLEZ SÉLECTIONNER AU MOINS UN DOCUMENT SOURCE"
            )
            return
            
        if not self.output_directory.get() or not os.path.isdir(self.output_directory.get()):
            messagebox.showerror(
                "ERREUR DE PROCÉDURE",
                "VEUILLEZ DÉSIGNER UN DOSSIER DE DESTINATION VALIDE"
            )
            return

        selected_lang = self.target_lang.get()
        lang_code = LANGUAGES.get(selected_lang, None)
        if not lang_code:
            messagebox.showerror(
                "ERREUR DE LANGUE",
                f"Langue cible '{selected_lang}' non prise en charge."
            )
            return
        
        # Vider la file d'attente d'affichage
        self.queue_display.config(state=tk.NORMAL)
        self.queue_display.delete(1.0, tk.END)
        self.queue_display.config(state=tk.DISABLED)
        
        self.root.event_generate('<<StartTranslation>>')