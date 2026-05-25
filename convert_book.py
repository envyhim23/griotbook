import argparse
import asyncio
import os
import sys
import glob

# Gestion de l'import résilient de PdfReader
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

import edge_tts
from processor import TextProcessor

async def synthesize_chunk(text, voice, rate_str, temp_path):
    communicate = edge_tts.Communicate(text, voice, rate=rate_str)
    await communicate.save(temp_path)

async def main_async(pdf_path, output_path, voice, speed):
    if not os.path.exists(pdf_path):
        print(f"Erreur : Le fichier PDF '{pdf_path}' n'existe pas.")
        sys.exit(1)
        
    print(f"📖 Chargement et lecture du PDF '{pdf_path}'...")
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"   {total_pages} page(s) détectée(s). Extraction du texte...")
        
        # Extraction du texte brut de toutes les pages
        all_text_list = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            all_text_list.append(text)
            
        full_raw_text = "\n\n".join(all_text_list)
        
    except Exception as e:
        print(f"Erreur lors de la lecture du PDF : {e}")
        sys.exit(1)
        
    print("⚙️ Analyse structurelle et nettoyage par expressions régulières (Regex)...")
    # Segmentation intelligente et nettoyage
    chunks = TextProcessor.process_and_segment(full_raw_text, chunk_size=2500)
    total_chunks = len(chunks)
    
    if total_chunks == 0:
        print("Erreur : Aucun texte exploitable trouvé dans le PDF.")
        sys.exit(1)
        
    print(f"   Texte découpé en {total_chunks} segment(s) de lecture fluide.")
    
    # Préparation du débit de voix
    speed_pct = int((speed - 1.0) * 100)
    rate_str = f"{speed_pct:+}%" if speed_pct != 0 else "+0%"
    
    temp_files = []
    print(f"🔊 Début de la synthèse vocale avec la voix '{voice}' (Vitesse: {speed}x)...")
    
    for i, chunk in enumerate(chunks, 1):
        temp_name = f"temp_chunk_{i}_{int(asyncio.get_event_loop().time())}.mp3"
        temp_files.append(temp_name)
        print(f"   [{i}/{total_chunks}] Synthèse du segment ({len(chunk)} caractères)...", end="", flush=True)
        
        try:
            await synthesize_chunk(chunk, voice, rate_str, temp_name)
            print(" OK")
        except Exception as e:
            print(" ERREUR")
            print(f"Erreur lors de la synthèse vocale : {e}")
            # Nettoyage des fichiers temporaires existants
            for f in temp_files:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception:
                        pass
            sys.exit(1)
            
    print(f"🔗 Fusion de tous les segments dans '{output_path}'...")
    try:
        # Fusion binaire
        with open(output_path, "wb") as outfile:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    with open(temp_file, "rb") as infile:
                        outfile.write(infile.read())
                    try:
                        os.remove(temp_file)  # Nettoyage immédiat
                    except Exception:
                        pass
                        
        print(f"🎉 Succès ! Le livre audio complet a été généré : '{output_path}'")
        
    except Exception as e:
        print(f"Erreur lors de la fusion des fichiers : {e}")
        # Nettoyage
        for f in temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Convertit un livre PDF en livre audio MP3 complet avec nettoyage et segmentation.")
    parser.add_argument("pdf", nargs="?", default="ebook.pdf", help="Chemin vers le fichier PDF d'entrée (par défaut: ebook.pdf)")
    parser.add_argument("output", nargs="?", default="audio_complet.mp3", help="Nom du fichier MP3 de sortie (par défaut: audio_complet.mp3)")
    parser.add_argument("--voice", default="fr-FR-DeniseNeural", help="Nom de la voix Edge-TTS (par défaut: fr-FR-DeniseNeural)")
    parser.add_argument("--speed", type=float, default=1.0, help="Vitesse de lecture de 0.5 à 2.0 (par défaut: 1.0)")
    
    args = parser.parse_args()
    
    # Validation du PDF fallback si par défaut
    pdf_file = args.pdf
    if not os.path.exists(pdf_file) and pdf_file == "ebook.pdf":
        pdfs = glob.glob("*.pdf")
        if pdfs:
            pdf_file = pdfs[0]
            print(f"💡 Fichier 'ebook.pdf' introuvable. Utilisation de '{pdf_file}' trouvé dans le dossier.")
            
    asyncio.run(main_async(pdf_file, args.output, args.voice, args.speed))

if __name__ == "__main__":
    main()
