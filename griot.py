import asyncio, os, glob, time
import gradio as gr
try: from pypdf import PdfReader
except ImportError: from PyPDF2 import PdfReader
import edge_tts
from processor import TextProcessor

VOICES = {"Français (Denise)": "fr-FR-DeniseNeural", "Français (Henri)": "fr-FR-HenriNeural", "Français (Eloise)": "fr-FR-EloiseNeural", "Canadien (Sylvie)": "fr-CA-SylvieNeural", "Canadien (Antoine)": "fr-CA-AntoineNeural", "Belge (Charline)": "fr-BE-CharlineNeural", "Anglais (Aria)": "en-US-AriaNeural", "Anglais (Guy)": "en-US-GuyNeural"}
CSS = "body,.gradio-container{font-family:'Outfit',sans-serif;background:#0b0f19!important;color:#e5e7eb!important}.title-container{text-align:center;margin-bottom:1rem;padding:1.5rem;background:linear-gradient(135deg,rgba(79,70,229,.1),rgba(139,92,246,.1));border-radius:16px;border:1px solid rgba(139,92,246,.15)}.title-container h1{font-weight:700;font-size:2.5rem;background:linear-gradient(to right,#a78bfa,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0}.glass-panel{background:rgba(17,25,40,.55)!important;backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.08)!important;border-radius:16px!important;padding:20px}.btn-primary{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:#fff!important;border:none!important;font-weight:600!important}.btn-secondary{background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.1)!important}textarea,input,select,.dropdown{background:rgba(10,15,26,.8)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:8px!important}.audio-player audio{width:100%!important;border-radius:24px!important;margin-top:10px}"

# --- Configuration de fiabilité ---
MAX_RETRIES = 3          # Nombre de tentatives par segment
BASE_DELAY = 2.0         # Délai de base entre les retries (secondes)
INTER_SEGMENT_DELAY = 1.5  # Pause entre segments pour éviter le rate-limiting
MAX_CONCURRENT = 2       # Nombre max de synthèses simultanées


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
            # Identifier si c'est une erreur 403 (rate-limit / token)
            is_403 = "403" in error_msg or "WSServerHandshakeError" in type(e).__name__
            if attempt < retries:
                delay = BASE_DELAY * (2 ** (attempt - 1))  # 2s, 4s, 8s
                if is_403:
                    delay *= 2  # Doubler le délai pour les 403
                print(f"   ⚠️ Tentative {attempt}/{retries} échouée ({type(e).__name__}). "
                      f"Nouvelle tentative dans {delay:.0f}s...")
                await asyncio.sleep(delay)
            else:
                print(f"   ❌ Échec après {retries} tentatives : {error_msg}")
    raise last_error


def clean_tmp():
    [os.remove(f) for f in glob.glob("tmp_*.mp3") if os.path.exists(f)]

def load_pdf(file):
    if not file: return "", gr.update(visible=False), 1, "Aucun fichier", []
    # Extraction et nettoyage dynamique en liste
    pages = ["\n\n".join(TextProcessor.process_and_segment(p.extract_text() or "", 3000)) or "[Page vide]" for p in PdfReader(file.name).pages]
    return pages[0] if pages else "", gr.update(visible=True), gr.update(maximum=len(pages)), f"{len(pages)} pages", pages

def update_page(num, pages):
    return pages[min(max(0, int(num)-1), len(pages)-1)], num

async def gen_audio(text, voice, speed, page_num=0):
    if not text or text == "[Page vide]": return None, "⚠️ Texte vide."
    clean_tmp()
    out = f"tmp_page_{page_num}_{int(time.time())}.mp3"
    rate_str = f"{int((speed-1)*100):+}%"
    try:
        await tts_with_retry(text, VOICES.get(voice), rate_str, out)
        return out, f"✅ Succès (Page {page_num})"
    except Exception as e:
        return None, f"❌ Erreur : {e}"

async def gen_full(pages, voice, speed, prog=gr.Progress()):
    if not pages: return None, "⚠️ Aucun PDF."
    chunks = TextProcessor.process_and_segment("\n".join(pages), 2500)
    clean_tmp()
    temps = [f"tmp_f_{i}.mp3" for i in range(len(chunks))]
    out = "audio_complet.mp3"
    rate_str = f"{int((speed-1)*100):+}%"
    voice_id = VOICES.get(voice)
    failed_segments = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def process_segment(i, chunk, tmp):
        async with semaphore:
            try:
                prog((i + 0.5) / len(chunks), desc=f"🔊 Synthèse segment {i+1}/{len(chunks)}...")
                await tts_with_retry(chunk, voice_id, rate_str, tmp)
                prog((i + 1) / len(chunks), desc=f"✅ Segment {i+1}/{len(chunks)} terminé")
                # Pause inter-segment pour éviter le rate-limiting
                await asyncio.sleep(INTER_SEGMENT_DELAY)
            except Exception as e:
                failed_segments.append((i + 1, str(e)))
                print(f"   ❌ Segment {i+1} définitivement échoué: {e}")

    # Exécuter les synthèses avec concurrence contrôlée
    tasks = [process_segment(i, chunk, tmp) for i, (chunk, tmp) in enumerate(zip(chunks, temps))]
    await asyncio.gather(*tasks)

    # Fusion binaire des segments réussis
    prog(0.95, desc="🔗 Fusion binaire...")
    with open(out, "wb") as f_out:
        for t in temps:
            if os.path.exists(t):
                with open(t, "rb") as f_in: f_out.write(f_in.read())
                os.remove(t)

    if failed_segments:
        details = ", ".join(f"#{s[0]}" for s in failed_segments)
        status = f"⚠️ Livre généré avec {len(failed_segments)} segment(s) manquant(s) : {details}"
    else:
        status = f"🎉 Livre complet généré avec succès ! ({len(chunks)} segments)"
    return out, status

with gr.Blocks(title="GriotBook") as demo:
    gr.HTML("<div class='title-container'><h1>📖 GriotBook</h1><p>Lecteur PDF Premium - Version Fiable et Ultra-Rapide</p></div>")
    state_pages, state_curr = gr.State([]), gr.State(1)

    with gr.Row(): file_input, lbl = gr.File(label="Importez votre livre PDF", file_types=[".pdf"]), gr.Label("Prêt", show_label=False)
    with gr.Row(visible=False) as panel:
        txt = gr.TextArea(label="Texte de la Page (Modifiable)", lines=18, interactive=True, scale=3, elem_classes="glass-panel")
        with gr.Column(scale=2, elem_classes="glass-panel"):
            voice, speed = gr.Dropdown(list(VOICES.keys()), value="Français (Denise)", label="Voix"), gr.Slider(0.5, 2.0, 1.0, 0.1, label="Vitesse")
            with gr.Row():
                btn_prev, num, btn_next = gr.Button("◀ Précédent", elem_classes="btn-secondary"), gr.Number(1, label="Page"), gr.Button("Suivant ▶", elem_classes="btn-secondary")

            btn_gen, aud, stat = gr.Button("🔊 Générer la page", elem_classes="btn-primary"), gr.Audio(elem_classes="audio-player"), gr.Textbox(label="Statut")
            btn_full, aud_full, stat_full = gr.Button("🚀 Générer livre complet", elem_classes="btn-primary"), gr.Audio(elem_classes="audio-player"), gr.Textbox(label="Statut global")

    file_input.change(load_pdf, file_input, [txt, panel, num, lbl, state_pages])
    btn_prev.click(lambda n: max(1, int(n)-1), num, num)
    btn_next.click(lambda n, p: min(len(p), int(n)+1), [num, state_pages], num)
    num.change(update_page, [num, state_pages], [txt, state_curr])
    btn_gen.click(gen_audio, [txt, voice, speed, state_curr], [aud, stat])
    btn_full.click(gen_full, [state_pages, voice, speed], [aud_full, stat_full])

if __name__ == "__main__":
    demo.launch(css=CSS,share=True)
