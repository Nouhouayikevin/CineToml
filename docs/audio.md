# 🔊 Documentation — Audio

## Musique de fond

```toml
[audio]
musique  = "./assets/sons/background.mp3"  # OBLIGATOIRE pour activer
volume   = 0.25      # 0.0 à 1.0 (défaut: 0.3)
debut    = "0:00"    # début de la musique MM:SS
fin      = "auto"    # "auto" ou MM:SS
fade_in  = 1.0       # fondu d'entrée en secondes
fade_out = 2.0       # fondu de sortie en secondes
```

**Formats acceptés :** `.mp3`, `.wav`, `.ogg`, `.m4a`

**Volume recommandé :** `0.2` à `0.3` — la musique doit être en fond, pas dominante.

---

## Bibliothèque de bruitages

```toml
[bruitages]
choc        = "./assets/sons/vine_boom.mp3"
fail        = "./assets/sons/faaaah.mp3"
win         = "./assets/sons/tada.mp3"
malaise     = "./assets/sons/oh_no.mp3"
suspense    = "./assets/sons/ominous.mp3"
rire        = "./assets/sons/laugh_track.mp3"
notification = "./assets/sons/ding.mp3"
```

**Utilisation dans les scènes :**
```toml
bruitage = "$choc"      # avec le préfixe $
```

---

## Sons gratuits recommandés

| Site | Description |
|---|---|
| [Mixkit.co](https://mixkit.co) | Sons gratuits haute qualité |
| [Zapsplat.com](https://zapsplat.com) | Grande bibliothèque gratuite |
| [Pixabay.com/music](https://pixabay.com/music) | Musiques libres de droits |
| [YouTube Audio Library](https://studio.youtube.com) | Musiques pour créateurs |

**Sons viraux populaires :**
- Vine Boom — choc/surprise
- Oh No (Kreepa) — malaise
- Bruh — réaction comique
- Ta-Da — victoire/twist positif
- Ominous Countdown — suspense

---

## TTS (Text-To-Speech)

Active la lecture vocale des messages dans les scènes SMS.

```toml
[[scenes]]
type = "sms"
tts  = true     # activer ici
messages = [...]
```

La voix utilisée est définie par personnage dans `[personnages.xxx.voix]`.

**Configuration ElevenLabs :**
```bash
export ELEVENLABS_API_KEY=ta_clé_api
```

**Configuration Bark (local) :**
```bash
pip install bark scipy
# Premier lancement = téléchargement des modèles (~5GB)
```
