import argparse, asyncio, os, glob
try: from pypdf import PdfReader
except ImportError: from PyPDF2 import PdfReader
import edge_tts
from processor import TextProcessor

# --- Configuration de fiabilité ---
MAX_RETRIES = 3          # Nombre de tentatives par segment
BASE_DELAY = 2.0         # Délai de base entre les retries (secondes)
INTER_SEGMENT_DELAY = 1.5  # Pause entre segments pour éviter le rate-limiting


async def tts_with_retry(text, voice, rate_str, output_file, retries=MAX_RETRIES):
    """Synthèse vocale avec retry automatique et backoff exponentiel."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate_str)
            await communicate.save(output_file)
            return True
        except Exception as e:
            last_error = e
            error_msg = str(e)
            is_403 = "403" in error_msg or "WSServerHandshakeError" in type(e).__name__
            if attempt < retries:
                delay = BASE_DELAY * (2 ** (attempt - 1))
                if is_403:
                    delay *= 2
                print(f"   ⚠️ Tentative {attempt}/{retries} échouée ({type(e).__name__}). "
                      f"Nouvelle tentative dans {delay:.0f}s...")
                await asyncio.sleep(delay)
            else:
                print(f"   ❌ Échec après {retries} tentatives : {error_msg}")
    raise last_error


async def main(pdf, out, voice, speed):
    pdf = pdf if os.path.exists(pdf) else (glob.glob("*.pdf")[0] if glob.glob("*.pdf") else None)
    if not pdf: return print("Erreur : Aucun fichier PDF trouvé.")

    print(f"📖 Chargement et nettoyage de '{pdf}'...")
    text = "\n\n".join(p.extract_text() or "" for p in PdfReader(pdf).pages)
    chunks = TextProcessor.process_and_segment(text, 2500)

    print(f"🔊 Synthèse vocale en cours ({len(chunks)} segments)...")
    temps = [f"tmp_chunk_{i}.mp3" for i in range(len(chunks))]
    rate_str = f"{int((speed - 1.0) * 100):+}%" if speed != 1.0 else "+0%"
    failed = []

    for i, (chunk, tmp_file) in enumerate(zip(chunks, temps)):
        try:
            await tts_with_retry(chunk, voice, rate_str, tmp_file)
            print(f"   ✅ Segment {i+1}/{len(chunks)} sauvegardé : {tmp_file}")
        except Exception as e:
            failed.append(i + 1)
            print(f"   ❌ Segment {i+1}/{len(chunks)} échoué définitivement : {e}")
        # Pause inter-segment pour éviter le rate-limiting
        if i < len(chunks) - 1:
            await asyncio.sleep(INTER_SEGMENT_DELAY)

    print(f"🔗 Fusion binaire dans '{out}'...")
    with open(out, "wb") as f_out:
        for t in temps:
            if os.path.exists(t):
                with open(t, "rb") as f_in: f_out.write(f_in.read())
                os.remove(t)

    if failed:
        print(f"⚠️ Livre généré avec {len(failed)} segment(s) manquant(s) : {failed}")
    else:
        print("🎉 Succès ! Livre audio complet généré.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Convertisseur PDF vers Audio")
    p.add_argument("pdf", nargs="?", default="ebook.pdf")
    p.add_argument("out", nargs="?", default="audio_complet.mp3")
    p.add_argument("--voice", default="fr-FR-DeniseNeural")
    p.add_argument("--speed", type=float, default=1.0)
    args = p.parse_args()
    asyncio.run(main(args.pdf, args.out, args.voice, args.speed))
