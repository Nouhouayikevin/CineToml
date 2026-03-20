# 🎬 CineToml

> Un langage de script basé sur TOML pour générer des vidéos virales automatiquement.

## C'est quoi CineToml ?

CineToml est un langage de script qui te permet de créer des **faceless videos virales** (fake SMS, conversations drôles, réactions) en écrivant simplement un fichier `.toml`.

Tu écris le script → tu lances une commande → tu obtiens une vidéo MP4 prête à publier.

```bash
python compiler/main.py examples/pizzas.toml
# ✅ output/pizzas.mp4 généré en 30 secondes
```

## 🚀 Fonctionnalités

- 💬 Conversations SMS style iMessage / WhatsApp / Telegram
- 🖼️ Scènes de réaction avec images et memes
- 🔊 Bruitages synchronisés (vine boom, faaaah, oh no...)
- 🎵 Musique de fond avec contrôle du volume
- 🗣️ Text-To-Speech automatique (voix qui lit les messages)
- 🎭 Effets visuels (zoom, shake, flash, bounce...)
- 📱 Interface réaliste (heure, batterie, signal)
- 🌍 Multi-langues et multi-formats

## 📦 Installation

```bash
git clone https://github.com/Nouhouayikevin/CineToml
cd CineToml
pip install -r requirements.txt
cd remotion-engine && npm install
```

## 📝 Exemple rapide

```toml
[meta]
title = "J'ai commandé 500 pizzas au boulot"
resolution = "9x16"
langue = "fr"

[personnages.moi]
couleur = "#0084FF"
cote = "right"

[personnages.chef]
couleur = "#3C3C3E"
cote = "left"

[[scenes]]
type = "titre"
texte = "J'ai commandé 500 pizzas 🍕"
duree = 3.0

[[scenes]]
type = "sms"
messages = [
  {perso = "moi", texte = "Chef j'ai fait une erreur..."},
  {perso = "chef", texte = "C'est quoi encore"},
  {perso = "moi", texte = "J'ai commandé 500 PIZZAS"},
]

[[scenes]]
type = "reaction"
media = "./assets/images/shocked.jpg"
bruitage = "$choc"
duree = 2.0
```

## 📚 Documentation

- [Démarrage rapide](docs/getting-started.md)
- [Types de scènes](docs/scenes.md)
- [Personnages](docs/personnages.md)
- [Audio](docs/audio.md)
- [Exemples](examples/)

## 🛠️ Stack technique

| Outil | Rôle |
|---|---|
| Python | Parser + orchestration |
| TOML | Langage de script |
| Remotion | Moteur de rendu vidéo |
| React | Rendu des composants |
| FFmpeg | Compilation finale |
| gTTS / ElevenLabs | Text-To-Speech |

## 📄 Licence

MIT — libre d'utilisation

---

> Créé par [@Nouhouayikevin](https://github.com/Nouhouayikevin) 🚀
