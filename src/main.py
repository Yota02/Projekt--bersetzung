import tkinter as tk
from gui.window import TranslatorWindow
from translation.translator import PDFTranslator
import threading

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.window = TranslatorWindow(self.root)
        self.translator = PDFTranslator(self.update_progress)
        self.root.bind('<<StartTranslation>>', self.handle_translation)
        
    def handle_translation(self, event):
        input_file = self.window.input_file.get()
        output_file = self.window.output_file.get()
        target_lang = self.window.target_lang.get()
        
        # Démarrer la traduction dans un thread séparé
        thread = threading.Thread(
            target=self.translator.translate,
            args=(input_file, output_file, target_lang)
        )
        thread.daemon = True
        thread.start()
    
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