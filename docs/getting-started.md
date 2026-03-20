# 🚀 Démarrage rapide — CineToml

## Prérequis

| Outil | Version minimale | Installation |
|---|---|---|
| Python | 3.11+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| FFmpeg | 4+ | `sudo apt install ffmpeg` |
| Git | any | `sudo apt install git` |

---

## Installation

**1. Clone le repo**
```bash
git clone https://github.com/Nouhouayikevin/CineToml
cd CineToml
```

**2. Installe les dépendances Python**
```bash
pip install -r requirements.txt
```

**3. Installe le moteur Remotion**
```bash
cd remotion-engine
npm install
cd ..
```

---

## Ta première vidéo en 3 minutes

**1. Copie l'exemple de base**
```bash
cp docs/exemples/basic.toml mon_script.toml
```

**2. Edite ton script**
```bash
nano mon_script.toml   # ou VS Code, vim, etc.
```

**3. Valide ton script (optionnel mais recommandé)**
```bash
python compiler/main.py mon_script.toml --validate-only
```

**4. Génère la vidéo !**
```bash
python compiler/main.py mon_script.toml
```

**5. Récupère ta vidéo**
```
output/mon_script.mp4  ✅
```

---

## Options de la commande

```bash
python compiler/main.py <fichier.toml> [options]

Options :
  -o, --output <path>   Chemin de sortie du MP4
  --no-tts              Désactive la voix off
  --validate-only       Valide sans générer
  --version             Affiche la version
```

**Exemples :**
```bash
# Sortie personnalisée
python compiler/main.py mon_script.toml -o ~/Videos/ma_video.mp4

# Sans voix off
python compiler/main.py mon_script.toml --no-tts

# Validation seule
python compiler/main.py mon_script.toml --validate-only
```

---

## Structure d'un projet CineToml

```
mon_projet/
├── script.toml          ← ton script
├── assets/
│   ├── sons/
│   │   ├── background.mp3
│   │   ├── vine_boom.mp3
│   │   └── faaaah.mp3
│   └── images/
│       ├── shocked.jpg
│       └── meme.jpg
└── output/
    └── script.mp4       ← vidéo générée
```

---

## Résoudre les erreurs courantes

| Erreur | Solution |
|---|---|
| `META_MISSING` | Ajoute la section `[meta]` dans ton .toml |
| `PERSO_UNDEFINED` | Vérifie que le nom du perso dans `messages` correspond à un `[personnages.xxx]` |
| `FILE_NOT_FOUND` | Vérifie que le path de ton image/son est correct |
| `npm: command not found` | Installe Node.js |
| `ffmpeg: command not found` | `sudo apt install ffmpeg` |

---

## Prochaine étape

→ Lis la [Spécification complète](../SPEC.md) pour découvrir toutes les options
→ Explore les [exemples](exemples/) pour t'inspirer
→ Consulte la [doc des scènes](scenes.md) pour les effets avancés
