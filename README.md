# 📚 GriotBook : Lecteur PDF Intelligent & Convertisseur de Livres Audio

GriotBook est un convertisseur de livres PDF en livres audio haute qualité, écrit entièrement en Python. Il utilise les voix neuronales avancées de **Microsoft Edge-TTS** pour générer une lecture fluide et naturelle.

L'application a été entièrement reconstruite pour être **ultra-légère** sur GitHub, **hautement performante** (zéro timeout) et dotée d'une interface graphique moderne de style *glassmorphic*.

---

## ✨ Fonctionnalités Clés

1. **Lecture Intelligente par Segmentation** :
   - **Gestion des césures** : Fusionne automatiquement les mots coupés par un tiret en fin de ligne (ex: `informa-` et `tion` $\to$ `information`).
   - **Reconstruction de texte** : Supprime les sauts de ligne artificiels des PDF pour recréer des phrases continues, tout en respectant les vrais paragraphes.
   - **Suppression du bruit** : Élimine automatiquement par regex les en-têtes, pieds de page et numéros de page isolés.

2. **Nettoyage Regex des Caractères Spéciaux** :
   - Filtre et supprime tous les symboles nuisibles à la lecture demandés : `###`, `***`, `(`, `)`, `&`, `%`, `@`, `?`, `"`, `.`, `>`, `<`, `/`, `}`, `{`, `+`, `_`, `-`, `\`, `|`, `^`, `$`, `!`, `~`.
   - Insère des espaces simples pour éviter de coller les mots et assure une prononciation claire.

3. **Génération de Livre Complet** :
   - Divise le texte en blocs logiques de taille optimale pour l'API.
   - Fusionne de manière asynchrone les segments audios générés pour produire un unique fichier final : **`audio_complet.mp3`**.
   - Ne nécessite aucune dépendance externe lourde (comme FFMpeg).

4. **Deux Modes de Fonctionnement (GUI et CLI)** :
   - **Interface Graphique Web (Gradio)** : Mode sombre premium avec navigation de pages, édition du texte extrait à la volée, choix de la voix, vitesse, et suivi en temps réel de la progression.
   - **Ligne de commande (CLI)** : Un script rapide et autonome pour lancer les conversions en une seule commande.

5. **Dépôt GitHub Optimisé** :
   - Intégration d'un fichier `.gitignore` robuste pour exclure l'environnement virtuel (`venv/`) et les fichiers MP3 temporaires. Le code source ne pèse que quelques kilo-octets.

---

## 🚀 Installation et Démarrage

### 1. Cloner le projet
```bash
git clone https://github.com/ton-pseudo/griotbook.git
cd griotbook
```

### 2. Configurer l'environnement virtuel
Créez et activez l'environnement virtuel Python :
* **Windows (PowerShell)** :
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
* **macOS / Linux** :
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

---

## 🎮 Utilisation

### Mode 1 : Interface Graphique (GUI)
Pour lancer l'application web interactive :
```bash
python griot.py
```
Ouvrez ensuite votre navigateur à l'adresse indiquée (généralement `http://127.0.0.1:7860`).
- **Fonctionnalités** : Glissez-déposez votre PDF, modifiez le texte de la page courante avant de lire, ajustez la vitesse, naviguez de page en page, ou cliquez sur **"Générer le livre entier"** pour télécharger le fichier `audio_complet.mp3` avec une barre de progression.

### Mode 2 : Ligne de Commande (CLI)
Pour convertir directement et rapidement un livre PDF sans lancer d'interface graphique :
```bash
# Utilisation par défaut (cherche un PDF dans le dossier et génère audio_complet.mp3)
python convert_book.py

# Utilisation personnalisée avec arguments
python convert_book.py chemin/vers/mon_livre.pdf sortie_audio.mp3 --voice fr-FR-HenriNeural --speed 1.1
```

---

## ⚙️ Configuration

### Voix disponibles par défaut :
- **Français (France)** : Denise (Femme), Henri (Homme), Eloise (Femme)
- **Canadien** : Sylvie (Femme), Antoine (Homme)
- **Belge** : Charline (Femme)
- **Anglais (US/GB)** : Aria, Guy, Sonia

### Ajustement de la vitesse :
Ajustable de `0.5x` (lent) à `2.0x` (rapide). La vitesse standard est de `1.0x`.
