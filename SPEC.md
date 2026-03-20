# 📋 CineToml — Spécification Officielle v1.0

> Ce document définit les règles strictes du langage CineToml.
> Tout fichier `.toml` qui ne respecte pas ces règles sera rejeté par le compilateur.

---

## 1. Structure globale d'un fichier CineToml

Un fichier CineToml valide doit contenir ces sections dans cet ordre :

```
[meta]           ← OBLIGATOIRE
[interface]      ← optionnel
[audio]          ← optionnel
[bruitages]      ← optionnel
[personnages.*]  ← OBLIGATOIRE si des scènes SMS existent
[[scenes]]       ← OBLIGATOIRE (au moins 1)
```

---

## 2. Section `[meta]`

**Obligatoire.** Définit les métadonnées globales de la vidéo.

```toml
[meta]
title = "Mon titre"         # OBLIGATOIRE — titre de la vidéo
langue = "fr"               # OBLIGATOIRE — code ISO (fr, en, es, de...)
resolution = "9x16"         # OBLIGATOIRE — "9x16" | "16x9" | "1x1"
fps = 30                    # optionnel — défaut: 30
author = "mon_pseudo"       # optionnel
watermark = "@moncompte"    # optionnel — affiché en bas de la vidéo
plateforme = ["tiktok"]     # optionnel — ["tiktok", "reels", "youtube"]
hook = "texte accrocheur"   # optionnel — les 3 premières secondes
cta = "Suivez pour plus 😂" # optionnel — call to action final
```

**Règles strictes :**
- `title` : max 100 caractères
- `langue` : doit être un code ISO 639-1 valide
- `resolution` : accepte uniquement `9x16`, `16x9`, `1x1`
- `fps` : accepte uniquement `24`, `30`, `60`

---

## 3. Section `[interface]`

**Optionnel.** Définit l'apparence de l'interface téléphone.

```toml
[interface]
style = "imessage"     # "imessage" | "whatsapp" | "telegram" | "android"
heure = "23:47"        # format HH:MM
batterie = 12          # 0-100 (faible = drama 😂)
signal = "faible"      # "plein" | "moyen" | "faible" | "absent"
notification = false   # affiche une notif en haut
theme = "sombre"       # "sombre" | "clair"
```

**Règles strictes :**
- `heure` : format strict `HH:MM` (ex: `"23:47"`)
- `batterie` : entier entre 0 et 100
- Si `style = "imessage"` → bulles bleues/grises automatiquement

---

## 4. Section `[audio]`

**Optionnel.** Définit la musique de fond globale.

```toml
[audio]
musique = "./assets/sons/background.mp3"  # path relatif ou absolu
volume = 0.3          # 0.0 à 1.0
debut = "0:00"        # format MM:SS
fin = "auto"          # "auto" ou format MM:SS
fade_in = 1.0         # durée du fade in en secondes
fade_out = 2.0        # durée du fade out en secondes
```

**Règles strictes :**
- Le fichier audio doit exister sinon erreur `AUDIO_NOT_FOUND`
- Formats acceptés : `.mp3`, `.wav`, `.ogg`, `.m4a`
- `volume` : float entre `0.0` et `1.0`

---

## 5. Section `[bruitages]`

**Optionnel.** Définit une bibliothèque de sons réutilisables.

```toml
[bruitages]
choc       = "./assets/sons/vine_boom.mp3"
suspense   = "./assets/sons/ominous.mp3"
fail       = "./assets/sons/faaaah.mp3"
win        = "./assets/sons/ta-da.mp3"
malaise    = "./assets/sons/oh_no.mp3"
rire       = "./assets/sons/laugh_track.mp3"
notification = "./assets/sons/ding.mp3"
```

**Utilisation dans les scènes :**
```toml
bruitage = "$choc"      # référence avec le préfixe $
# au lieu de :
bruitage = "./assets/sons/vine_boom.mp3"
```

---

## 6. Section `[personnages]`

**Obligatoire** si des scènes de type `sms` existent.

```toml
[personnages.moi]
nom    = "Moi"           # optionnel — affiché dans l'interface
couleur = "#0084FF"      # OBLIGATOIRE — couleur de la bulle (hex)
cote   = "right"         # OBLIGATOIRE — "right" | "left"
voix   = "gtts"          # optionnel — "gtts" | "bark" | "elevenlabs:nom"
avatar = "./assets/images/avatar.png"  # optionnel

[personnages.chef]
nom    = "CHEF"
couleur = "#3C3C3E"
cote   = "left"
voix   = "gtts"
```

**Règles strictes :**
- Chaque personnage doit avoir un identifiant unique (ex: `moi`, `chef`)
- `couleur` : format hex strict `#RRGGBB`
- `cote` : uniquement `"right"` ou `"left"`
- Un fichier ne peut pas avoir deux personnages du même côté avec la même couleur

---

## 7. Section `[[scenes]]`

**Obligatoire.** Définit les scènes de la vidéo dans l'ordre.

### 7.1 Types de scènes

| Type | Description |
|---|---|
| `titre` | Écran titre avec texte centré |
| `sms` | Conversation SMS animée |
| `reaction` | Image ou vidéo de réaction |
| `focus` | Zoom sur une bulle précise |
| `outro` | Écran de fin |

---

### 7.2 Type `titre`

```toml
[[scenes]]
type      = "titre"
texte     = "J'ai commandé 500 pizzas 🍕"  # OBLIGATOIRE
duree     = 3.0                              # secondes — défaut: 3.0
fond      = "#000000"                        # couleur de fond
bruitage  = "$suspense"                      # son au démarrage
animation = "fade_in"                        # "fade_in" | "zoom_in" | "bounce"
taille_texte = 72                            # pixels — défaut: 72
```

---

### 7.3 Type `sms`

```toml
[[scenes]]
type     = "sms"
messages = [
  {perso = "moi",  texte = "Chef j'ai fait une erreur"},
  {perso = "chef", texte = "C'est quoi encore"},
  {perso = "moi",  texte = "J'ai commandé 500 PIZZAS 🍕"},
]
vitesse       = 80      # frames entre chaque message — défaut: 80
tts           = false   # activer la lecture vocale — défaut: false
fond_video    = "./assets/videos/background.mp4"  # optionnel
fond_image    = "./assets/images/background.jpg"  # optionnel
fond_opacite  = 0.4     # opacité du fond — défaut: 0.4
```

**Format d'un message :**
```toml
{perso = "id_personnage", texte = "contenu"}

# Avec image :
{perso = "moi", image = "./assets/images/photo.jpg"}

# Avec sticker :
{perso = "moi", sticker = "😱"}

# Avec bruitage sur ce message précis :
{perso = "chef", texte = "TU ES VIRÉ", bruitage = "$choc"}

# Avec effet sur ce message :
{perso = "moi", texte = "500 PIZZAS", effet = "shake"}
```

**Règles strictes :**
- `perso` doit référencer un personnage défini dans `[personnages]`
- Un message doit avoir soit `texte`, soit `image`, soit `sticker`
- `vitesse` : entier entre `20` et `200`

---

### 7.4 Type `reaction`

```toml
[[scenes]]
type     = "reaction"
media    = "./assets/images/shocked.jpg"  # OBLIGATOIRE — image ou vidéo
duree    = 2.0                             # secondes — OBLIGATOIRE
bruitage = "$fail"                         # optionnel
effet    = "zoom_in"                       # optionnel
texte_overlay = "😭😭😭"                  # texte par-dessus l'image
```

**Effets disponibles :**

| Effet | Description |
|---|---|
| `zoom_in` | Zoom progressif vers l'avant |
| `zoom_out` | Dézoom progressif |
| `shake` | Tremblement d'écran |
| `flash` | Flash blanc |
| `bounce` | Rebond |
| `fade_in` | Apparition en fondu |
| `fade_out` | Disparition en fondu |

---

### 7.5 Type `focus`

```toml
[[scenes]]
type         = "focus"
scene_ref    = 2          # id de la scène SMS à zoomer
message_index = 3         # index du message à zoomer (commence à 0)
duree        = 1.5
bruitage     = "$choc"
effet        = "shake"
```

---

### 7.6 Type `outro`

```toml
[[scenes]]
type      = "outro"
texte     = "Suivez pour plus 😂"  # OBLIGATOIRE
duree     = 3.0
animation = "fade_out"
bruitage  = "$win"
fond      = "#000000"
```

---

## 8. Règles globales du compilateur

### Erreurs fatales (arrêt de la compilation)
- `META_MISSING` : section `[meta]` absente
- `SCENE_MISSING` : aucune scène définie
- `PERSO_UNDEFINED` : personnage utilisé dans SMS mais non défini
- `FILE_NOT_FOUND` : fichier audio/image/vidéo introuvable
- `INVALID_RESOLUTION` : résolution non supportée
- `DUPLICATE_SCENE_ID` : deux scènes avec le même `id`

### Avertissements (compilation continue)
- `AUDIO_VOLUME_HIGH` : volume > 0.8 (risque de saturation)
- `SCENE_TOO_SHORT` : scène de moins de 0.5 secondes
- `NO_OUTRO` : pas de scène `outro` définie
- `NO_HOOK` : `hook` non défini dans `[meta]`

---

## 9. Variables spéciales

```toml
# Dans n'importe quel champ texte :
texte = "Vidéo par {meta.author}"     # référence aux métadonnées
texte = "Scène {scene.id} sur {total_scenes}"
```

---

## 10. Exemple complet valide

```toml
[meta]
title      = "J'ai commandé 500 pizzas au boulot"
langue     = "fr"
resolution = "9x16"
fps        = 30
watermark  = "@moncompte"

[interface]
style    = "imessage"
heure    = "14:32"
batterie = 87
theme    = "sombre"

[audio]
musique = "./assets/sons/background.mp3"
volume  = 0.25
fade_in = 1.0
fade_out = 2.0

[bruitages]
choc     = "./assets/sons/vine_boom.mp3"
fail     = "./assets/sons/faaaah.mp3"
win      = "./assets/sons/tada.mp3"

[personnages.moi]
couleur = "#0084FF"
cote    = "right"
voix    = "gtts"

[personnages.chef]
nom     = "CHEF"
couleur = "#3C3C3E"
cote    = "left"
voix    = "gtts"

[[scenes]]
type      = "titre"
texte     = "J'ai commandé 500 pizzas au boulot 🍕"
duree     = 3.0
bruitage  = "$fail"
animation = "fade_in"

[[scenes]]
type  = "sms"
messages = [
  {perso = "moi",  texte = "Chef j'ai fait une petite erreur"},
  {perso = "chef", texte = "C'est quoi encore"},
  {perso = "moi",  texte = "J'ai commandé 500 PIZZAS 🍕", bruitage = "$choc"},
]
vitesse = 80

[[scenes]]
type     = "reaction"
media    = "./assets/images/shocked.jpg"
duree    = 2.0
bruitage = "$fail"
effet    = "zoom_in"

[[scenes]]
type  = "sms"
messages = [
  {perso = "chef", texte = "TU ES VIRÉ", effet = "shake"},
  {perso = "moi",  texte = "Même si j'ai commandé des desserts ?"},
  {perso = "chef", texte = "...tu es augmenté"},
]

[[scenes]]
type      = "outro"
texte     = "Suivez pour plus 😂"
duree     = 3.0
animation = "fade_out"
bruitage  = "$win"
```

---

*CineToml v1.0 — Spécification rédigée par [@Nouhouayikevin](https://github.com/Nouhouayikevin)*
