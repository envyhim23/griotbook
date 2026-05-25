import asyncio
import os
import glob
import gradio as gr
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader
import edge_tts

# Voix Edge-TTS haute qualité proposées par défaut
VOICES = {
    "Français - Denise (Femme)": "fr-FR-DeniseNeural",
    "Français - Henri (Homme)": "fr-FR-HenriNeural",
    "Français - Eloise (Femme)": "fr-FR-EloiseNeural",
    "Canadien - Sylvie (Femme)": "fr-CA-SylvieNeural",
    "Canadien - Antoine (Homme)": "fr-CA-AntoineNeural",
    "Belge - Charline (Femme)": "fr-BE-CharlineNeural",
    "Anglais (US) - Aria (Femme)": "en-US-AriaNeural",
    "Anglais (US) - Guy (Homme)": "en-US-GuyNeural",
    "Anglais (GB) - Sonia (Femme)": "en-GB-SoniaNeural",
}

# CSS customisé premium (Thème Sombre & Effet Verre Dépoli)
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Styles Généraux */
body, .gradio-container {
    font-family: 'Outfit', -apple-system, sans-serif !important;
    background-color: #0b0f19 !important;
    color: #e5e7eb !important;
}

/* En-tête de l'application */
.title-container {
    text-align: center;
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%) !important;
    border-radius: 16px;
    border: 1px solid rgba(139, 92, 246, 0.15) !important;
}

.title-container h1 {
    font-weight: 700 !important;
    font-size: 2.6rem !important;
    background: linear-gradient(to right, #a78bfa, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 !important;
}

.title-container p {
    color: #9ca3af !important;
    font-size: 1.1rem !important;
    margin-top: 0.5rem !important;
}

/* Panneaux d'interface (Glassmorphic) */
.glass-panel {
    background: rgba(17, 25, 40, 0.55) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
}

/* Boutons principaux */
.btn-primary {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.2rem !important;
    cursor: pointer;
    transition: all 0.2s ease-in-out !important;
    box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.3) !important;
}

.btn-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.5) !important;
}

/* Boutons secondaires */
.btn-secondary {
    background: rgba(255, 255, 255, 0.06) !important;
    color: #f3f4f6 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.2s ease !important;
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.12) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

/* Zones de texte, entrées et listes déroulantes */
textarea, input[type="text"], input[type="number"], select, .dropdown {
    background-color: rgba(10, 15, 26, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #f3f4f6 !important;
    border-radius: 8px !important;
}

textarea:focus, input:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.15) !important;
}

/* Lecteur Audio Custom */
.audio-player audio {
    width: 100% !important;
    border-radius: 24px !important;
    margin-top: 10px;
}
"""

def cleanup_temp_files():
    """Supprime les fichiers audio temporaires créés lors des lectures précédentes."""
    for f in glob.glob("temp_audio_*.mp3"):
        try:
            os.remove(f)
        except Exception:
            pass

def load_pdf(file):
    """Charge le PDF, extrait les textes de toutes les pages et retourne les infos initiales."""
    if file is None:
        return "", gr.update(visible=False), gr.update(value=1, maximum=1), "Aucun fichier chargé", []
    
    try:
        reader = PdfReader(file.name)
        total_pages = len(reader.pages)
        
        # Extraction et nettoyage du texte de chaque page
        page_texts = []
        for page in reader.pages:
            text = page.extract_text() or ""
            clean_lines = [line.strip() for line in text.split("\n")]
            clean_text = "\n".join([l for l in clean_lines if l])
            page_texts.append(clean_text)
            
        first_page_text = page_texts[0] if page_texts else "[Page vide]"
        
        return (
            first_page_text, 
            gr.update(visible=True), 
            gr.update(value=1, maximum=total_pages, minimum=1), 
            f"Fichier chargé : {total_pages} page(s) trouvée(s)", 
            page_texts
        )
    except Exception as e:
        return f"Erreur lors du décodage du PDF : {str(e)}", gr.update(visible=False), gr.update(value=1, maximum=1), "Erreur de chargement", []

def jump_to_page(page_num, page_texts):
    """Récupère le texte de la page demandée."""
    if not page_texts:
        return "", 1
    
    total = len(page_texts)
    page_num = max(1, min(total, int(page_num)))
    
    text = page_texts[page_num - 1]
    if not text.strip():
        text = "[Page vide]"
        
    return text, page_num

def go_prev_val(current_val):
    """Décrémente le numéro de page."""
    return max(1, current_val - 1)

def go_next_val(current_val, page_texts):
    """Incrémente le numéro de page."""
    total = len(page_texts) if page_texts else 1
    return min(total, current_val + 1)

async def generate_audio(text, voice_key, speed, page_num):
    """Génère le fichier MP3 pour le texte de la page active."""
    if not text or text.strip() in ("", "[Page vide]"):
        return None, "Le texte de cette page est vide."
        
    voice = VOICES.get(voice_key, "fr-FR-DeniseNeural")
    
    # Calcul du taux de vitesse (ex: +10%, -5%, +0%)
    speed_pct = int((speed - 1.0) * 100)
    rate_str = f"{speed_pct:+}%" if speed_pct != 0 else "+0%"
    
    cleanup_temp_files()
    
    # Génère un fichier avec un nom unique (évite le cache navigateur)
    out_chemin = f"temp_audio_{page_num}_{int(asyncio.get_event_loop().time())}.mp3"
    
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate_str)
        await communicate.save(out_chemin)
        
        if os.path.exists(out_chemin) and os.path.getsize(out_chemin) > 0:
            return out_chemin, f"Succès : Audio généré pour la page {page_num}."
        else:
            return None, "Erreur lors de la génération de l'audio."
            
    except Exception as e:
        return None, f"Erreur Edge-TTS : {str(e)}"

# Construction de l'interface Gradio
with gr.Blocks(title="GriotBook - Lecteur PDF Premium") as demo:
    # En-tête
    gr.HTML(
        """
        <div class="title-container">
            <h1>📖 GriotBook</h1>
            <p>Convertissez vos livres PDF en audio page par page de façon fluide et performante</p>
        </div>
        """
    )
    
    # Variables d'état Gradio
    page_texts_state = gr.State([])
    current_page_state = gr.State(1)
    
    # Zone d'importation
    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Importez votre livre PDF", file_types=[".pdf"])
            status_lbl = gr.Label("Prêt", show_label=False)
            
    # Interface principale (Affichée uniquement après import)
    with gr.Row(visible=False) as controls_panel:
        # Colonne de Gauche : Liseur de texte
        with gr.Column(scale=3, elem_classes=["glass-panel"]):
            gr.Markdown("### 📝 Texte Extrait (Modifiable)")
            page_text_area = gr.TextArea(
                label="", 
                placeholder="Le texte de la page apparaîtra ici...",
                lines=18,
                interactive=True
            )
            
        # Colonne de Droite : Options de Voix et Audio
        with gr.Column(scale=2, elem_classes=["glass-panel"]):
            gr.Markdown("### ⚙️ Paramètres de Lecture")
            
            voice_select = gr.Dropdown(
                choices=list(VOICES.keys()), 
                value="Français - Denise (Femme)", 
                label="Voix de synthèse"
            )
            
            speed_slider = gr.Slider(
                minimum=0.5, 
                maximum=2.0, 
                value=1.0, 
                step=0.1, 
                label="Vitesse (1.0x = standard)"
            )
            
            gr.Markdown("---")
            gr.Markdown("### 🎛️ Navigation")
            
            with gr.Row():
                prev_btn = gr.Button("◀ Précédent", elem_classes=["btn-secondary"])
                page_indicator = gr.Number(value=1, label="Page", precision=0, interactive=True)
                next_btn = gr.Button("Suivant ▶", elem_classes=["btn-secondary"])
                
            gr.Markdown("---")
            gr.Markdown("### 🔊 Lecteur")
            
            generate_btn = gr.Button("Générer l'audio de cette page", elem_classes=["btn-primary"])
            audio_output = gr.Audio(label="Livre Audio", type="filepath", elem_classes=["audio-player"])
            status_output = gr.Textbox(label="Statut de l'audio", interactive=False)

    # Câblage des événements
    
    # 1. Chargement du PDF
    file_input.change(
        fn=load_pdf, 
        inputs=file_input, 
        outputs=[page_text_area, controls_panel, page_indicator, status_lbl, page_texts_state]
    )
    
    # 2. Navigation : Bouton Précédent
    prev_btn.click(
        fn=go_prev_val, 
        inputs=page_indicator, 
        outputs=page_indicator
    )
    
    # 3. Navigation : Bouton Suivant
    next_btn.click(
        fn=go_next_val, 
        inputs=[page_indicator, page_texts_state], 
        outputs=page_indicator
    )
    
    # 4. Changement de page (déclenché par saisie manuelle ou boutons)
    page_indicator.change(
        fn=jump_to_page, 
        inputs=[page_indicator, page_texts_state], 
        outputs=[page_text_area, current_page_state]
    )
    
    # 5. Génération Audio
    generate_btn.click(
        fn=generate_audio, 
        inputs=[page_text_area, voice_select, speed_slider, current_page_state], 
        outputs=[audio_output, status_output]
    )

if __name__ == "__main__":
    demo.launch(css=CSS)