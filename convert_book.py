import argparse, asyncio, os, glob
try: from pypdf import PdfReader
except ImportError: from PyPDF2 import PdfReader
import edge_tts
from processor import TextProcessor

async def main(pdf, out, voice, speed):
    pdf = pdf if os.path.exists(pdf) else (glob.glob("*.pdf")[0] if glob.glob("*.pdf") else None)
    if not pdf: return print("Erreur : Aucun fichier PDF trouvé.")
    
    print(f"📖 Chargement et nettoyage de '{pdf}'...")
    text = "\n\n".join(p.extract_text() or "" for p in PdfReader(pdf).pages)
    chunks = TextProcessor.process_and_segment(text, 2500)
    
    print(f"🔊 Synthèse vocale en cours ({len(chunks)} segments)...")
    temps = [f"tmp_chunk_{i}.mp3" for i in range(len(chunks))]
    rate_str = f"{int((speed - 1.0) * 100):+}%" if speed != 1.0 else "+0%"
    
    for chunk, tmp_file in zip(chunks, temps):
        await edge_tts.Communicate(chunk, voice, rate=rate_str).save(tmp_file)
        print(f"   -> Segment sauvegardé : {tmp_file}")
        
    print(f"🔗 Fusion binaire dans '{out}'...")
    with open(out, "wb") as f_out:
        for t in temps:
            if os.path.exists(t):
                with open(t, "rb") as f_in: f_out.write(f_in.read())
                os.remove(t)
    print("🎉 Succès ! Livre audio complet généré.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Convertisseur PDF vers Audio")
    p.add_argument("pdf", nargs="?", default="ebook.pdf")
    p.add_argument("out", nargs="?", default="audio_complet.mp3")
    p.add_argument("--voice", default="fr-FR-DeniseNeural")
    p.add_argument("--speed", type=float, default=1.0)
    args = p.parse_args()
    asyncio.run(main(args.pdf, args.out, args.voice, args.speed))
