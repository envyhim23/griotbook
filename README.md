# 📖 GriotBook

> Convertisseur de livres PDF en livres audio — 100% Python, ultra-léger et performant.

GriotBook transforme n'importe quel fichier PDF en livre audio haute qualité grâce aux voix neuronales de **Microsoft Edge-TTS**. Le texte est nettoyé intelligemment par regex avant la synthèse vocale.

---

## ⚡ Points Forts

- **Ultra-léger** : Seulement 3 fichiers Python (~120 lignes au total) et 3 dépendances.
- **Zéro timeout** : Lecture page par page ou par segments intelligents — fonctionne même sur des livres de 1000+ pages.
- **Nettoyage intelligent** : Regex compilées en C pour supprimer les caractères spéciaux, reconstruire les césures et filtrer le bruit de mise en page (numéros de page, en-têtes).
- **Deux modes** : Interface web premium (Gradio) ou ligne de commande rapide.
- **Aucune dépendance lourde** : Pas besoin de FFMpeg — fusion binaire native des MP3.

---

## 🚀 Installation

```bash
git clone https://github.com/envyhim23/griotbook.git
cd griotbook
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

---

## 🎮 Utilisation

### Interface Web (GUI)
```bash
python griot.py
```
Ouvrez `http://127.0.0.1:7860` dans votre navigateur.
- Glissez-déposez votre PDF
- Naviguez page par page et modifiez le texte extrait
- Choisissez la voix et la vitesse
- Générez l'audio d'une seule page ou du **livre entier** (`audio_complet.mp3`)

### Ligne de Commande (CLI)
```bash
# Par défaut : cherche un PDF dans le dossier → audio_complet.mp3
python convert_book.py

# Personnalisé
python convert_book.py mon_livre.pdf sortie.mp3 --voice fr-FR-HenriNeural --speed 1.2
```

---

## 📁 Structure du Projet

```
griotebook/
├── griot.py           # Interface web Gradio (62 lignes)
├── convert_book.py    # Script CLI de conversion (36 lignes)
├── processor.py       # Moteur de nettoyage regex & segmentation (19 lignes)
├── requirements.txt   # 3 dépendances uniquement
├── .gitignore         # Exclut venv/ et fichiers audio
└── README.md
```

---

## ⚙️ Voix Disponibles

| Langue | Voix |
|--------|------|
| Français (France) | Denise (F), Henri (H), Eloise (F) |
| Français (Canada) | Sylvie (F), Antoine (H) |
| Français (Belgique) | Charline (F) |
| Anglais (US) | Aria (F), Guy (H) |

Vitesse ajustable de `0.5x` à `2.0x` (standard : `1.0x`).

---

## 🛠️ Dépendances

| Package | Rôle |
|---------|------|
| `gradio` | Interface web interactive |
| `edge-tts` | Synthèse vocale Microsoft (gratuit, sans clé API) |
| `pypdf` | Extraction de texte depuis les fichiers PDF |

> `asyncio` et `textwrap` sont utilisés mais font partie de la bibliothèque standard Python — aucune installation nécessaire.
