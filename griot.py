import asyncio
import edge_tts
from PyPDF2 import PdfReader
import gradio as gr
import os

# Choix d'une voix stable
VOICE = "fr-FR-DeniseNeural"

async def convert_large_pdf(pdf_file):
    if pdf_file is None:
        return None, "Erreur : Aucun fichier fourni."

    # 1. Extraction et nettoyage
    text_blocks = []
    try:
        reader = PdfReader(pdf_file.name)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                # On nettoie un peu le texte pour éviter les caractères invisibles lourds
                clean_content = " ".join(content.split())
                text_blocks.append(clean_content)
    except Exception as e:
        return None, f"Erreur PDF : {str(e)}"

    full_text = " ".join(text_blocks)
    if len(full_text) < 10:
        return None, "Texte trop court ou illisible."

    # 2. Préparation du fichier
    out_chemin = "output_audio.mp3"

    # 3. Utilisation de Communicate avec gestion de flux (Stream)
    # Cela évite d'attendre la fin de la génération complète pour commencer à écrire
    try:
        communicate = edge_tts.Communicate(full_text, VOICE)
        
        # On ouvre le fichier en mode binaire
        with open(out_chemin, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
        
        return out_chemin, f"Succès ! {len(full_text)} caractères traités."
    
    except Exception as e:
        return None, f"Erreur de Timeout/Réseau : {str(e)}"

def ui_wrapper(pdf_file):
    # On utilise une nouvelle boucle d'événement pour éviter les conflits Gradio
    return asyncio.run(convert_large_pdf(pdf_file))

# Interface Gradio
with gr.Blocks() as demo:
    gr.Markdown("# 📖 Lecteur PDF Longue Durée")
    file_input = gr.File(label="Charger un livre PDF")
    btn = gr.Button("Générer l'audio")
    audio_output = gr.Audio(label="Livre Audio", type="filepath")
    status = gr.Textbox(label="Statut")

    btn.click(fn=ui_wrapper, inputs=file_input, outputs=[audio_output, status])

demo.launch()