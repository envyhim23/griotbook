# 📚 GriotBook : Lecteur d'Ebook Haute Qualité

Une application web interactive conçue avec **Gradio** qui transforme vos fichiers PDF en livres audio fluides et naturels, utilisant la technologie neuronale de **Microsoft Edge-TTS**.

## ✨ Caractéristiques
- **Voix Naturelles** : Utilise les voix de Microsoft Edge pour un rendu humain (fini les voix robotiques).
- **Interface Intuitive** : Une application web simple pour glisser-déposer vos PDF.
- **Optimisé pour les PDF longs** : Gestion des timeouts et nettoyage du texte pour une lecture sans interruption.

## 🚀 Installation et Utilisation

### 1. Cloner le projet
```bash
git clone https://github.com/envyhim23/griotbook.git
cd griotbook
```

### 2. Environnement virtuel
```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 3. Lancer l'interface Gradio
```bash
python griot.py
```

Ouvrez l'URL affichée dans le terminal (souvent `http://127.0.0.1:7860`).

### 4. Ligne de commande (livre audio complet)
```bash
python convert_book.py mon_livre.pdf sortie.mp3 --voice fr-FR-DeniseNeural --speed 1.0
```

## 📁 Version web audio (sans Gradio)

La nouvelle interface **audio uniquement** (FastAPI, sans timeout) est dans le dossier séparé :

**`../griotbook-audio/`** — voir son `README.md`.
