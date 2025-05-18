import tkinter as tk
from gui.window import TranslatorWindow
from translation.translator import PDFTranslator
import threading
import os
from queue import Queue

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.window = TranslatorWindow(self.root)
        self.translator = PDFTranslator(self.update_progress)
        self.root.bind('<<StartTranslation>>', self.handle_translation)
        self.translation_queue = Queue()
        self.currently_translating = False
        self.current_file_index = 0
        self.total_files = 0
        
    def handle_translation(self, event):
        input_files = self.window.input_files
        output_dir = self.window.output_directory.get()
        target_lang = self.window.target_lang.get()
        
        # Vider la file d'attente actuelle et ajouter les nouveaux fichiers
        while not self.translation_queue.empty():
            self.translation_queue.get()
        
        self.total_files = len(input_files)
        self.current_file_index = 0
        
        # Ajouter tous les fichiers à la file d'attente
        for input_file in input_files:
            filename = os.path.basename(input_file)
            base_name = os.path.splitext(filename)[0]
            output_file = os.path.join(output_dir, f"{base_name}_traduit.pdf")
            
            self.translation_queue.put({
                'input': input_file,
                'output': output_file,
                'lang': target_lang
            })
            
            self.window.add_to_queue_display(input_file, output_file, target_lang)
        
        # Si aucune traduction n'est en cours, démarrer la première
        if not self.currently_translating:
            self.process_next_translation()
    
    def process_next_translation(self):
        if not self.translation_queue.empty():
            self.currently_translating = True
            job = self.translation_queue.get()
            
            self.current_file_index += 1
            self.window.log(f"Début de la traduction du fichier {self.current_file_index}/{self.total_files}: {os.path.basename(job['input'])}")
            self.window.update_queue_status(self.current_file_index, self.total_files)
            
            # Démarrer la traduction dans un thread séparé
            thread = threading.Thread(
                target=self.translate_file,
                args=(job['input'], job['output'], job['lang'])
            )
            thread.daemon = True
            thread.start()
        else:
            self.currently_translating = False
            self.window.log("Toutes les traductions sont terminées.")
            self.window.update_queue_status(0, 0)
            
    def translate_file(self, input_file, output_file, target_lang):
        try:
            self.translator.translate(input_file, output_file, target_lang)
            self.window.log(f"Traduction terminée: {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
            self.window.mark_file_completed(input_file)
        except Exception as e:
            self.window.log(f"Erreur lors de la traduction de {os.path.basename(input_file)}: {str(e)}")
        finally:
            # Passer au fichier suivant
            self.root.after(1000, self.process_next_translation)
    
    def update_progress(self, progress=None, message=None):
        if message is not None:
            self.window.log(message)
        if progress is not None:
            self.window.progress['value'] = progress
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()