"""
CineToml Parser v1.0
Lit, valide et retourne la structure d'un fichier .toml CineToml
"""

import tomllib
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────
# Couleurs terminal
# ─────────────────────────────────────────
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def error(msg):   print(f"{RED}{BOLD}[ERREUR]{RESET} {msg}"); sys.exit(1)
def warn(msg):    print(f"{YELLOW}[AVERTISSEMENT]{RESET} {msg}")
def success(msg): print(f"{GREEN}[OK]{RESET} {msg}")
def info(msg):    print(f"{BLUE}[INFO]{RESET} {msg}")

# ─────────────────────────────────────────
# Constantes de validation
# ─────────────────────────────────────────
RESOLUTIONS_VALIDES  = ["9x16", "16x9", "1x1"]
FPS_VALIDES          = [24, 30, 60]
STYLES_VALIDES       = ["imessage", "whatsapp", "telegram", "android"]
THEMES_VALIDES       = ["sombre", "clair"]
COTES_VALIDES        = ["right", "left"]
TYPES_SCENES_VALIDES = ["titre", "sms", "reaction", "focus", "outro"]
EFFETS_VALIDES       = ["zoom_in", "zoom_out", "shake", "flash", "bounce", "fade_in", "fade_out"]
ANIMATIONS_VALIDES   = ["fade_in", "zoom_in", "bounce", "fade_out"]
FORMATS_AUDIO_VALIDES = [".mp3", ".wav", ".ogg", ".m4a"]
FORMATS_IMAGE_VALIDES = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
FORMATS_VIDEO_VALIDES = [".mp4", ".mov", ".webm"]
SIGNAUX_VALIDES      = ["plein", "moyen", "faible", "absent"]
VOIX_VALIDES_PREFIX  = ["gtts", "bark", "elevenlabs"]


# ─────────────────────────────────────────
# Classe principale CineTomlParser
# ─────────────────────────────────────────
class CineTomlParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.base_dir = os.path.dirname(os.path.abspath(filepath))
        self.data = {}
        self.errors = []
        self.warnings = []

    # ── Chargement ──────────────────────────
    def load(self) -> dict:
        if not os.path.exists(self.filepath):
            error(f"FILE_NOT_FOUND — Fichier introuvable : {self.filepath}")

        if not self.filepath.endswith(".toml"):
            error(f"INVALID_FORMAT — Le fichier doit avoir l'extension .toml")

        with open(self.filepath, "rb") as f:
            try:
                self.data = tomllib.load(f)
                success(f"Fichier chargé : {self.filepath}")
            except tomllib.TOMLDecodeError as e:
                error(f"TOML_SYNTAX_ERROR — Erreur de syntaxe TOML :\n  {e}")

        return self.validate()

    # ── Validation principale ────────────────
    def validate(self) -> dict:
        info("Validation du fichier CineToml...")

        self._validate_meta()
        self._validate_interface()
        self._validate_audio()
        self._validate_bruitages()
        self._validate_personnages()
        self._validate_scenes()

        self._afficher_bilan()
        return self.data

    # ── [meta] ───────────────────────────────
    def _validate_meta(self):
        if "meta" not in self.data:
            error("META_MISSING — La section [meta] est obligatoire")

        meta = self.data["meta"]

        # Champs obligatoires
        for champ in ["title", "langue", "resolution"]:
            if champ not in meta:
                error(f"META_MISSING_FIELD — Champ obligatoire manquant dans [meta] : '{champ}'")

        # Validation title
        if len(meta["title"]) > 100:
            error("META_TITLE_TOO_LONG — Le titre ne peut pas dépasser 100 caractères")

        # Validation resolution
        if meta["resolution"] not in RESOLUTIONS_VALIDES:
            error(f"INVALID_RESOLUTION — Résolution '{meta['resolution']}' non supportée. Valeurs acceptées : {RESOLUTIONS_VALIDES}")

        # Validation fps
        fps = meta.get("fps", 30)
        if fps not in FPS_VALIDES:
            error(f"INVALID_FPS — FPS '{fps}' non supporté. Valeurs acceptées : {FPS_VALIDES}")
        self.data["meta"]["fps"] = fps  # injecter la valeur par défaut

        # Avertissements optionnels
        if "hook" not in meta:
            warn("NO_HOOK — 'hook' non défini dans [meta]. Recommandé pour maximiser l'engagement.")
        if "watermark" not in meta:
            warn("NO_WATERMARK — 'watermark' non défini dans [meta].")

        success("[meta] valide")

    # ── [interface] ──────────────────────────
    def _validate_interface(self):
        if "interface" not in self.data:
            return  # optionnel

        interface = self.data["interface"]

        if "style" in interface and interface["style"] not in STYLES_VALIDES:
            error(f"INVALID_STYLE — Style '{interface['style']}' non supporté. Valeurs : {STYLES_VALIDES}")

        if "theme" in interface and interface["theme"] not in THEMES_VALIDES:
            error(f"INVALID_THEME — Thème '{interface['theme']}' non supporté. Valeurs : {THEMES_VALIDES}")

        if "batterie" in interface:
            b = interface["batterie"]
            if not isinstance(b, int) or b < 0 or b > 100:
                error("INVALID_BATTERY — 'batterie' doit être un entier entre 0 et 100")
            if b <= 15:
                info(f"🔋 Batterie à {b}% — bonne ambiance drama !")

        if "heure" in interface:
            heure = interface["heure"]
            parts = heure.split(":")
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                error(f"INVALID_TIME — Format d'heure invalide '{heure}'. Format attendu : HH:MM")

        if "signal" in interface and interface["signal"] not in SIGNAUX_VALIDES:
            error(f"INVALID_SIGNAL — Signal '{interface['signal']}' non supporté. Valeurs : {SIGNAUX_VALIDES}")

        success("[interface] valide")

    # ── [audio] ──────────────────────────────
    def _validate_audio(self):
        if "audio" not in self.data:
            return  # optionnel

        audio = self.data["audio"]

        if "musique" in audio:
            self._check_file(audio["musique"], FORMATS_AUDIO_VALIDES, "AUDIO_NOT_FOUND")

        if "volume" in audio:
            v = audio["volume"]
            if not isinstance(v, (int, float)) or v < 0.0 or v > 1.0:
                error("INVALID_VOLUME — 'volume' doit être un float entre 0.0 et 1.0")
            if v > 0.8:
                warn("AUDIO_VOLUME_HIGH — Volume > 0.8, risque de saturation audio")

        success("[audio] valide")

    # ── [bruitages] ──────────────────────────
    def _validate_bruitages(self):
        if "bruitages" not in self.data:
            self.data["bruitages"] = {}
            return

        for nom, path in self.data["bruitages"].items():
            self._check_file(path, FORMATS_AUDIO_VALIDES, "BRUITAGE_NOT_FOUND", nom)

        success(f"[bruitages] valide — {len(self.data['bruitages'])} son(s) défini(s)")

    # ── [personnages] ────────────────────────
    def _validate_personnages(self):
        if "personnages" not in self.data:
            self.data["personnages"] = {}
            return

        personnages = self.data["personnages"]

        for id_perso, perso in personnages.items():
            # Champs obligatoires
            if "couleur" not in perso:
                error(f"PERSO_MISSING_FIELD — Personnage '{id_perso}' : champ 'couleur' manquant")
            if "cote" not in perso:
                error(f"PERSO_MISSING_FIELD — Personnage '{id_perso}' : champ 'cote' manquant")

            # Validation couleur hex
            couleur = perso["couleur"]
            if not couleur.startswith("#") or len(couleur) != 7:
                error(f"INVALID_COLOR — Personnage '{id_perso}' : couleur '{couleur}' invalide. Format : #RRGGBB")

            # Validation côté
            if perso["cote"] not in COTES_VALIDES:
                error(f"INVALID_COTE — Personnage '{id_perso}' : côté '{perso['cote']}' invalide. Valeurs : {COTES_VALIDES}")

            # Validation voix
            if "voix" in perso:
                voix = perso["voix"]
                valide = any(voix.startswith(v) for v in VOIX_VALIDES_PREFIX)
                if not valide:
                    error(f"INVALID_VOICE — Personnage '{id_perso}' : voix '{voix}' invalide. Préfixes valides : {VOIX_VALIDES_PREFIX}")

        success(f"[personnages] valide — {len(personnages)} personnage(s) défini(s)")

    # ── [[scenes]] ───────────────────────────
    def _validate_scenes(self):
        if "scenes" not in self.data:
            error("SCENE_MISSING — Aucune scène définie. Au moins une [[scenes]] est obligatoire")

        scenes = self.data["scenes"]
        ids_vus = []

        for i, scene in enumerate(scenes):
            # Injection d'un id si absent
            if "id" not in scene:
                scene["id"] = i + 1

            sid = scene["id"]

            # Vérif doublon
            if sid in ids_vus:
                error(f"DUPLICATE_SCENE_ID — Deux scènes ont le même id : {sid}")
            ids_vus.append(sid)

            # Type obligatoire
            if "type" not in scene:
                error(f"SCENE_MISSING_TYPE — Scène {sid} : champ 'type' manquant")

            stype = scene["type"]
            if stype not in TYPES_SCENES_VALIDES:
                error(f"INVALID_SCENE_TYPE — Scène {sid} : type '{stype}' invalide. Valeurs : {TYPES_SCENES_VALIDES}")

            # Validation selon le type
            if stype == "titre":
                self._validate_scene_titre(scene)
            elif stype == "sms":
                self._validate_scene_sms(scene)
            elif stype == "reaction":
                self._validate_scene_reaction(scene)
            elif stype == "focus":
                self._validate_scene_focus(scene)
            elif stype == "outro":
                self._validate_scene_outro(scene)

        # Avertissement pas d'outro
        types = [s["type"] for s in scenes]
        if "outro" not in types:
            warn("NO_OUTRO — Aucune scène 'outro' définie. Recommandé pour le CTA.")

        success(f"[[scenes]] valide — {len(scenes)} scène(s)")

    def _validate_scene_titre(self, scene):
        sid = scene["id"]
        if "texte" not in scene:
            error(f"SCENE_MISSING_FIELD — Scène titre {sid} : champ 'texte' manquant")
        self._check_effet(scene, sid)
        self._check_bruitage(scene, sid)
        duree = scene.get("duree", 3.0)
        scene["duree"] = duree
        if duree < 0.5:
            warn(f"SCENE_TOO_SHORT — Scène {sid} : durée {duree}s très courte")

    def _validate_scene_sms(self, scene):
        sid = scene["id"]
        if "messages" not in scene:
            error(f"SCENE_MISSING_FIELD — Scène sms {sid} : champ 'messages' manquant")

        personnages = self.data.get("personnages", {})
        bruitages = self.data.get("bruitages", {})

        for j, msg in enumerate(scene["messages"]):
            if "perso" not in msg:
                error(f"MSG_MISSING_PERSO — Scène {sid}, message {j} : champ 'perso' manquant")
            if msg["perso"] not in personnages:
                error(f"PERSO_UNDEFINED — Scène {sid}, message {j} : personnage '{msg['perso']}' non défini dans [personnages]")
            if "texte" not in msg and "image" not in msg and "sticker" not in msg:
                error(f"MSG_EMPTY — Scène {sid}, message {j} : doit avoir 'texte', 'image' ou 'sticker'")
            if "image" in msg:
                self._check_file(msg["image"], FORMATS_IMAGE_VALIDES, "MSG_IMAGE_NOT_FOUND")
            if "bruitage" in msg:
                self._resolve_bruitage(msg["bruitage"], bruitages, f"Scène {sid} message {j}")
            if "effet" in msg and msg["effet"] not in EFFETS_VALIDES:
                error(f"INVALID_EFFET — Scène {sid}, message {j} : effet '{msg['effet']}' invalide")

        vitesse = scene.get("vitesse", 80)
        if not isinstance(vitesse, int) or vitesse < 20 or vitesse > 200:
            error(f"INVALID_VITESSE — Scène {sid} : 'vitesse' doit être un entier entre 20 et 200")

        if "fond_video" in scene:
            self._check_file(scene["fond_video"], FORMATS_VIDEO_VALIDES, "FOND_VIDEO_NOT_FOUND")
        if "fond_image" in scene:
            self._check_file(scene["fond_image"], FORMATS_IMAGE_VALIDES, "FOND_IMAGE_NOT_FOUND")

    def _validate_scene_reaction(self, scene):
        sid = scene["id"]
        if "media" not in scene:
            error(f"SCENE_MISSING_FIELD — Scène reaction {sid} : champ 'media' manquant")
        if "duree" not in scene:
            error(f"SCENE_MISSING_FIELD — Scène reaction {sid} : champ 'duree' manquant")

        ext = os.path.splitext(scene["media"])[1].lower()
        formats_valides = FORMATS_IMAGE_VALIDES + FORMATS_VIDEO_VALIDES
        self._check_file(scene["media"], formats_valides, "MEDIA_NOT_FOUND")
        self._check_effet(scene, sid)
        self._check_bruitage(scene, sid)

        if scene["duree"] < 0.5:
            warn(f"SCENE_TOO_SHORT — Scène {sid} : durée {scene['duree']}s très courte")

    def _validate_scene_focus(self, scene):
        sid = scene["id"]
        for champ in ["scene_ref", "message_index", "duree"]:
            if champ not in scene:
                error(f"SCENE_MISSING_FIELD — Scène focus {sid} : champ '{champ}' manquant")
        self._check_bruitage(scene, sid)
        self._check_effet(scene, sid)

    def _validate_scene_outro(self, scene):
        sid = scene["id"]
        if "texte" not in scene:
            error(f"SCENE_MISSING_FIELD — Scène outro {sid} : champ 'texte' manquant")
        duree = scene.get("duree", 3.0)
        scene["duree"] = duree
        self._check_bruitage(scene, sid)

    # ── Helpers ──────────────────────────────
    def _check_file(self, path, formats_valides, code_erreur, nom=None):
        """Vérifie qu'un fichier existe et a un format valide"""
        ext = os.path.splitext(path)[1].lower()
        if ext not in formats_valides:
            label = f"'{nom}'" if nom else f"'{path}'"
            error(f"{code_erreur} — Format {label} invalide '{ext}'. Formats acceptés : {formats_valides}")

        full_path = path if os.path.isabs(path) else os.path.join(self.base_dir, path)
        if not os.path.exists(full_path):
            label = f"'{nom}' ({path})" if nom else f"'{path}'"
            warn(f"{code_erreur} — Fichier {label} introuvable. Vérifie le path.")

    def _check_bruitage(self, scene, sid):
        """Résout et valide un bruitage dans une scène"""
        if "bruitage" not in scene:
            return
        bruitages = self.data.get("bruitages", {})
        self._resolve_bruitage(scene["bruitage"], bruitages, f"Scène {sid}")

    def _resolve_bruitage(self, bruitage, bruitages, contexte):
        """Résout $nom → path réel"""
        if bruitage.startswith("$"):
            nom = bruitage[1:]
            if nom not in bruitages:
                error(f"BRUITAGE_UNDEFINED — {contexte} : bruitage '{bruitage}' non défini dans [bruitages]")
        else:
            self._check_file(bruitage, FORMATS_AUDIO_VALIDES, "BRUITAGE_NOT_FOUND")

    def _check_effet(self, scene, sid):
        if "effet" in scene and scene["effet"] not in EFFETS_VALIDES:
            error(f"INVALID_EFFET — Scène {sid} : effet '{scene['effet']}' invalide. Valeurs : {EFFETS_VALIDES}")
        if "animation" in scene and scene["animation"] not in ANIMATIONS_VALIDES:
            error(f"INVALID_ANIMATION — Scène {sid} : animation '{scene['animation']}' invalide. Valeurs : {ANIMATIONS_VALIDES}")

    # ── Bilan final ──────────────────────────
    def _afficher_bilan(self):
        print()
        print(f"{BOLD}{'─'*50}{RESET}")
        print(f"{BOLD}  ✅ CineToml valide !{RESET}")
        print(f"{'─'*50}")
        meta = self.data["meta"]
        scenes = self.data.get("scenes", [])
        persos = self.data.get("personnages", {})
        print(f"  📽️  Titre      : {meta['title']}")
        print(f"  📐  Résolution : {meta['resolution']} @ {meta['fps']}fps")
        print(f"  🌍  Langue     : {meta['langue']}")
        print(f"  🎬  Scènes     : {len(scenes)}")
        print(f"  👤  Personnages: {len(persos)}")
        print(f"{'─'*50}")
        print()


# ─────────────────────────────────────────
# Point d'entrée standalone
# ─────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python parser.py <fichier.toml>")
        sys.exit(1)

    parser = CineTomlParser(sys.argv[1])
    data = parser.load()
    print(data)
