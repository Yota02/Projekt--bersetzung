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
        self.root.title("Projekt Übersetzung - Empire Translator")
        self.root.geometry("700x600")
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
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
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
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # En-tête avec sceau impérial
        header_frame = ttk.Frame(main_frame, style='Empire.TFrame')
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        if self.imperial_seal:
            seal_label = ttk.Label(header_frame, image=self.imperial_seal)
            seal_label.grid(row=0, column=0, padx=10)

        title_label = ttk.Label(header_frame,
                              text="BUREAU IMPÉRIAL DE TRADUCTION\nSECTION 203",
                              font=('Times New Roman', 20, 'bold'),
                              foreground='#D4B886',
                              background='#2B2D32',
                              justify='center')
        title_label.grid(row=0, column=1, pady=10)

        # Cadre des documents
        doc_frame = ttk.Frame(main_frame, style='Empire.TFrame')
        doc_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # Section document source
        ttk.Label(doc_frame,
                 text="DOCUMENT SOURCE:",
                 style='Empire.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(doc_frame,
                 textvariable=self.input_file,
                 width=60,
                 style='Empire.TEntry').grid(row=0, column=1, padx=5)
        ttk.Button(doc_frame,
                  text="LOCALISER",
                  command=self._browse_input,
                  style='Empire.TButton').grid(row=0, column=2)

        # Section document de sortie
        ttk.Label(doc_frame,
                 text="ARCHIVE DE DESTINATION:",
                 style='Empire.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(doc_frame,
                 textvariable=self.output_file,
                 width=60,
                 style='Empire.TEntry').grid(row=1, column=1, padx=5)
        ttk.Button(doc_frame,
                  text="DÉSIGNER",
                  command=self._browse_output,
                  style='Empire.TButton').grid(row=1, column=2)

        # Section langue
        lang_frame = ttk.Frame(main_frame, style='Empire.TFrame')
        lang_frame.grid(row=2, column=0, columnspan=3, pady=20)

        ttk.Label(lang_frame,
                 text="LANGUE CIBLE:",
                 style='Empire.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        lang_combo = ttk.Combobox(lang_frame,
                                textvariable=self.target_lang,
                                values=list(LANGUAGES.keys()),
                                width=30,
                                state='readonly')
        lang_combo.grid(row=0, column=1, sticky=tk.W, padx=5)

        # Barre de progression
        self.progress = ttk.Progressbar(main_frame,
                                      length=600,
                                      mode='determinate',
                                      style='Empire.Horizontal.TProgressbar')
        self.progress.grid(row=3, column=0, columnspan=3, pady=20)

        # Bouton d'exécution
        execute_button = ttk.Button(main_frame,
                                  text="EXÉCUTER LA TRADUCTION",
                                  command=self.start_translation,
                                  style='Empire.TButton')
        execute_button.grid(row=4, column=0, columnspan=3, pady=10)

        # Zone de rapport
        log_frame = ttk.Frame(main_frame, style='Empire.TFrame')
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))

        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(log_frame,
                              height=10,
                              width=70,
                              bg='#1A1B1E',
                              fg='#D4B886',
                              font=('Courier New', 10),
                              yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        # Configuration du redimensionnement
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _browse_input(self):
        filename = filedialog.askopenfilename(
            title="SÉLECTION DU DOCUMENT SOURCE",
            filetypes=[("Documents PDF", "*.pdf")]
        )
        if filename:
            self.input_file.set(filename)
            output = filename.rsplit('.', 1)[0] + '_traduit.docx'
            self.output_file.set(output)

    def _browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="DÉSIGNATION DE L'ARCHIVE DE DESTINATION",
            defaultextension=".docx",
            filetypes=[("Documents Word", "*.docx")]
        )
        if filename:
            self.output_file.set(filename)

    def log(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_text.insert(tk.END, f"{timestamp} {message}\n")
        self.log_text.see(tk.END)

    def start_translation(self):
        if not self.input_file.get() or not self.output_file.get():
            messagebox.showerror(
                "ERREUR DE PROCÉDURE",
                "VEUILLEZ DÉSIGNER LES DOCUMENTS SOURCE ET DE DESTINATION"
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

        self.root.event_generate('<<StartTranslation>>')