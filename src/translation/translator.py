from pdf2docx import Converter
from docx import Document
from deep_translator import GoogleTranslator
import time
import os
import re
from docx2pdf import convert

class PDFTranslator:
    def __init__(self, callback=None):
        self.callback = callback
        
    def translate(self, pdf_path, output_path, target_lang='fr'):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Le fichier {pdf_path} n'existe pas.")

        # S'assurer que l'extension de sortie est .pdf
        if not output_path.lower().endswith('.pdf'):
            output_path = os.path.splitext(output_path)[0] + '.pdf'

        temp_docx = 'temp_document.docx'
        temp_translated_docx = 'temp_translated_document.docx'
        
        self._log("Conversion du PDF en DOCX...")
        cv = Converter(pdf_path)
        cv.convert(temp_docx)
        cv.close()
        
        self._log("Début de la traduction...")
        doc = Document(temp_docx)
        
        # Convertir les noms de langues
        lang_map = {
            'German': 'de',
            'Japanese': 'ja',
            'French': 'fr',
            'English': 'en',
            'Russian': 'ru',
            'Italian': 'it'
        }
        
        lang_code = lang_map.get(target_lang, target_lang)
        if not lang_code:
            raise ValueError(f"Langue cible '{target_lang}' non prise en charge.")

        self._log("Début de la traduction...")
        translator = GoogleTranslator(source='auto', target=lang_code)
        
        # Amélioration: regrouper les paragraphes courts pour un meilleur contexte
        paragraphs = self._preprocess_paragraphs(doc.paragraphs)
        
        total_paragraphs = len(paragraphs)
        for i, para_data in enumerate(paragraphs, 1):
            text = para_data["text"].strip()
            if text:
                try:
                    # Préservation des structures spéciales
                    text_with_markers, special_markers = self._preprocess_text(text)
                    
                    # Amélioration: traduction du texte complet pour maintenir le contexte
                    try:
                        translated_text = translator.translate(text_with_markers)
                        time.sleep(0.5)  # Pause pour éviter les limitations d'API
                    except Exception as e:
                        self._log(f"Erreur lors de la traduction: {str(e)}")
                        # Essayer avec une approche alternative si la traduction échoue
                        translated_text = self._translate_in_chunks(translator, text_with_markers)
                    
                    # Restauration des éléments spéciaux
                    translated_text = self._postprocess_text(translated_text, special_markers)
                    
                    # Appliquer la traduction aux paragraphes d'origine
                    for idx in para_data["indices"]:
                        if idx < len(doc.paragraphs):
                            doc.paragraphs[idx].text = translated_text
                            
                    progress = (i / total_paragraphs) * 100
                    self._log(f"Progression: {i}/{total_paragraphs} segments traités")
                    if self.callback:
                        self.callback(progress)
                    
                except Exception as e:
                    self._log(f"Erreur lors de la traduction du segment {i}: {str(e)}")
                    continue
        
        self._log("Sauvegarde du document traduit au format DOCX temporaire...")
        doc.save(temp_translated_docx)
        
        self._log("Conversion du DOCX traduit en PDF...")
        try:
            convert(temp_translated_docx, output_path)
            self._log(f"Traduction terminée! Fichier PDF sauvegardé sous: {output_path}")
        except Exception as e:
            self._log(f"Erreur lors de la conversion en PDF: {str(e)}")
            self._log("Sauvegarde du document traduit au format DOCX uniquement...")
            # Si la conversion PDF échoue, conserver au moins le DOCX
            docx_output = os.path.splitext(output_path)[0] + '.docx'
            os.rename(temp_translated_docx, docx_output)
            self._log(f"Fichier DOCX sauvegardé sous: {docx_output}")
        
        # Nettoyage des fichiers temporaires
        if os.path.exists(temp_docx):
            os.remove(temp_docx)
        
        if os.path.exists(temp_translated_docx) and os.path.exists(output_path):
            os.remove(temp_translated_docx)
    
    def _preprocess_paragraphs(self, paragraphs):
        """
        Regroupe les paragraphes courts pour une meilleure cohérence de traduction
        Retourne une liste de dictionnaires contenant le texte combiné et les indices des paragraphes d'origine
        """
        processed_paragraphs = []
        current_text = ""
        current_indices = []
        min_paragraph_length = 200
        max_paragraph_length = 1500
        
        for i, para in enumerate(paragraphs):
            text = para.text.strip()
            if not text:  # Ignorer les paragraphes vides
                continue
                
            # Si le paragraphe est trop court, on le combine avec le texte actuel
            if len(current_text) + len(text) < max_paragraph_length:
                if current_text:
                    current_text += " " + text
                else:
                    current_text = text
                current_indices.append(i)
            else:
                # Si on a assez de texte, on l'ajoute à la liste
                if current_text:
                    processed_paragraphs.append({"text": current_text, "indices": current_indices})
                # On commence un nouveau groupe
                current_text = text
                current_indices = [i]
        
        # Ajouter le dernier groupe s'il existe
        if current_text:
            processed_paragraphs.append({"text": current_text, "indices": current_indices})
            
        return processed_paragraphs
    
    def _translate_in_chunks(self, translator, text):
        """
        Traduit le texte en morceaux si la traduction complète échoue
        """
        # Division en phrases
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Regrouper les phrases en chunks d'une taille raisonnable
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < 1000:  # Taille maximale de chunk
                current_chunk += sentence + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
                
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        # Traduire chaque chunk
        translated_chunks = []
        for chunk in chunks:
            try:
                translated_chunk = translator.translate(chunk)
                translated_chunks.append(translated_chunk)
                time.sleep(0.5)  # Pause entre les chunks
            except Exception as e:
                self._log(f"Erreur de traduction d'un chunk: {str(e)}")
                translated_chunks.append(chunk)  # Garder l'original en cas d'erreur
                
        # Joindre les chunks traduits
        return " ".join(translated_chunks)
    
    def _preprocess_text(self, text):
        """
        Prétraite le texte pour identifier et marquer les structures spéciales
        comme les dialogues, les noms propres, etc.
        """
        special_markers = {}
        
        # Capturer les dialogues entre guillemets
        dialogue_pattern = r'([«"].*?[»"])'
        dialogues = re.findall(dialogue_pattern, text)
        
        marked_text = text
        for i, dialogue in enumerate(dialogues):
            marker = f"__DIALOGUE_{i}__"
            special_markers[marker] = dialogue
            marked_text = marked_text.replace(dialogue, marker)
        
        # Capture d'autres éléments spéciaux comme les dates, les nombres, etc.
        # Date pattern (e.g. 12/05/2023)
        date_pattern = r'\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b'
        dates = re.findall(date_pattern, marked_text)
        
        for i, date in enumerate(dates):
            marker = f"__DATE_{i}__"
            special_markers[marker] = date
            marked_text = marked_text.replace(date, marker)
            
        return marked_text, special_markers
    
    def _postprocess_text(self, translated_text, special_markers):
        """
        Restaure les éléments spéciaux dans le texte traduit
        """
        result = translated_text
        
        # Restaurer tous les marqueurs spéciaux
        for marker, original in special_markers.items():
            if marker in result:
                result = result.replace(marker, original)
                
        return result
    
    def _log(self, message):
        if self.callback:
            self.callback(message=message)
        print(message)