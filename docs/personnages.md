# 👤 Documentation — Personnages

## Définir un personnage

Chaque personnage qui parle dans une scène SMS doit être défini dans `[personnages]`.

```toml
[personnages.moi]
nom     = "Moi"           # affiché dans le header (optionnel)
couleur = "#0084FF"       # OBLIGATOIRE — couleur hex de la bulle
cote    = "right"         # OBLIGATOIRE — "right" | "left"
voix    = "gtts"          # moteur TTS (optionnel)
avatar  = "./assets/images/avatar.png"  # photo de profil (optionnel)
```

## Couleurs recommandées

| Style | Côté droit | Côté gauche |
|---|---|---|
| iMessage | `#0084FF` | `#3C3C3E` |
| WhatsApp | `#25D366` | `#2A2A2A` |
| Telegram | `#2AABEE` | `#333333` |
| Android  | `#1A73E8` | `#3C3C3E` |

## Moteurs de voix (TTS)

| Valeur | Description | Coût |
|---|---|---|
| `gtts` | Google TTS — simple, requiert internet | Gratuit |
| `bark` | Bark — local, émotionnel, lent | Gratuit |
| `elevenlabs:rachel` | ElevenLabs — ultra réaliste | Payant |
| `elevenlabs:adam` | ElevenLabs voix masculine | Payant |

## Exemple complet

```toml
[personnages.moi]
nom     = "Kevin"
couleur = "#0084FF"
cote    = "right"
voix    = "gtts"

[personnages.boss]
nom     = "BOSS"
couleur = "#3C3C3E"
cote    = "left"
voix    = "bark"

[personnages.ami]
nom     = "Aminata"
couleur = "#25D366"
cote    = "left"
voix    = "elevenlabs:bella"
```

## Règles strictes
- Identifiant unique par personnage (ex: `moi`, `chef`, `ami`)
- Couleur au format `#RRGGBB` strict
- `cote` : uniquement `"right"` ou `"left"`
- Pas deux personnages avec le même côté et la même couleur
