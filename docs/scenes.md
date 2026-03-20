# 🎬 Documentation des scènes CineToml

## Vue d'ensemble

CineToml supporte 5 types de scènes :

| Type | Description | Obligatoire |
|---|---|---|
| `titre` | Écran titre animé | Non |
| `sms` | Conversation SMS | Oui (au moins 1) |
| `reaction` | Image/vidéo de réaction | Non |
| `focus` | Zoom sur une bulle | Non |
| `outro` | Écran de fin | Recommandé |

---

## `titre` — Écran titre

Affiche un texte centré sur fond noir avec animation.

```toml
[[scenes]]
type         = "titre"
texte        = "J'ai commandé 500 pizzas 🍕"  # OBLIGATOIRE
duree        = 3.0                              # secondes (défaut: 3.0)
fond         = "#000000"                        # couleur fond (défaut: noir)
taille_texte = 72                               # taille police (défaut: 72)
animation    = "fade_in"                        # fade_in | zoom_in | bounce
bruitage     = "$suspense"                      # son au démarrage
```

**Animations disponibles :**
- `fade_in` — apparition en fondu
- `zoom_in` — apparition avec zoom
- `bounce` — apparition avec rebond

---

## `sms` — Conversation SMS

Le cœur de CineToml. Affiche des bulles SMS animées.

```toml
[[scenes]]
type          = "sms"
vitesse       = 80           # frames entre chaque bulle (défaut: 80)
tts           = false        # activer la voix off (défaut: false)
fond_video    = "./assets/videos/bg.mp4"    # vidéo en arrière-plan
fond_image    = "./assets/images/bg.jpg"    # image en arrière-plan
fond_opacite  = 0.4          # opacité du fond (défaut: 0.4)

messages = [
  {perso = "moi",  texte = "Message normal"},
  {perso = "chef", texte = "Réponse normale"},

  # Message avec bruitage
  {perso = "moi", texte = "CHOC !", bruitage = "$choc"},

  # Message avec effet visuel
  {perso = "chef", texte = "TU ES VIRÉ", effet = "shake"},

  # Message avec image
  {perso = "moi", image = "./assets/images/photo.jpg"},

  # Sticker emoji
  {perso = "chef", sticker = "😱"},
]
```

**Effets de bulle disponibles :**
- `shake` — tremblement de la bulle à l'apparition

**Vitesse recommandée :**
- `60` — très rapide (contenu dynamique)
- `80` — normal (défaut)
- `100` — posé (suspense)
- `120+` — lent (drama)

---

## `reaction` — Image ou vidéo de réaction

Coupe la conversation pour montrer une image/vidéo drôle.

```toml
[[scenes]]
type          = "reaction"
media         = "./assets/images/shocked.jpg"  # OBLIGATOIRE
duree         = 2.0                             # secondes — OBLIGATOIRE
bruitage      = "$fail"                         # son de réaction
effet         = "zoom_in"                       # effet visuel
texte_overlay = "😭😭😭"                       # texte par-dessus
```

**Effets disponibles :**

| Effet | Description |
|---|---|
| `zoom_in` | Zoom progressif pendant la scène |
| `zoom_out` | Dézoom progressif |
| `shake` | Tremblement d'écran |
| `flash` | Flash blanc |
| `bounce` | Rebond à l'apparition |
| `fade_in` | Apparition en fondu |
| `fade_out` | Disparition en fondu |

**Formats media acceptés :**
- Images : `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- Vidéos : `.mp4`, `.mov`, `.webm`

---

## `focus` — Zoom sur une bulle

Zoome sur un message précis pour le mettre en valeur.

```toml
[[scenes]]
type          = "focus"
scene_ref     = 2    # id de la scène SMS contenant le message
message_index = 3    # index du message (commence à 0)
duree         = 1.5  # secondes
bruitage      = "$choc"
effet         = "shake"
```

Utile pour mettre en avant les moments clés de la conversation.

---

## `outro` — Écran de fin

Termine la vidéo avec un appel à l'action.

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

## Bonnes pratiques

**Structure narrative recommandée :**
```
titre (3s)
  ↓
sms — accroche (2-3 messages)
  ↓
reaction — première réaction (2s)
  ↓
sms — développement
  ↓
reaction — réaction au choc (2s)
  ↓
sms — twist final
  ↓
outro (3s)
```

**Timing :**
- Vidéo idéale : **30 à 60 secondes**
- Pas plus de 20 messages par scène SMS
- Alterner SMS et réactions toutes les 4-6 bulles
