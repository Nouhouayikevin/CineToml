"""
CineToml TTS Engine v1.0
Génère les fichiers audio pour chaque message SMS
Supporte : gTTS (gratuit), Bark (local), ElevenLabs (API)
"""

import os
import sys
import hashlib
import json
import shutil

RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def error(msg):   print(f"{RED}{BOLD}[TTS ERREUR]{RESET} {msg}"); sys.exit(1)
def warn(msg):    print(f"{YELLOW}[TTS WARN]{RESET} {msg}")
def success(msg): print(f"{GREEN}[TTS OK]{RESET} {msg}")
def info(msg):    print(f"{BLUE}[TTS INFO]{RESET} {msg}")

CACHE_FILE = ".cinetoml_tts_cache.json"

def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def cache_key(texte: str, langue: str, voix: str) -> str:
    return hashlib.md5(f"{texte}|{langue}|{voix}".encode()).hexdigest()


# ─── Backends TTS ───────────────────────────────────────────────────────────

def generer_gtts(texte: str, langue: str, output_path: str) -> bool:
    try:
        from gtts import gTTS
    except ImportError:
        error("gTTS non installé. Lance : pip install gtts")
    try:
        gTTS(text=texte, lang=langue, slow=False).save(output_path)
        return True
    except Exception as e:
        warn(f"gTTS échoué : {e}")
        return False

BARK_VOICES = {"fr": "v2/fr_speaker_0", "en": "v2/en_speaker_6", "es": "v2/es_speaker_0"}

def generer_bark(texte: str, langue: str, output_path: str) -> bool:
    try:
        from bark import SAMPLE_RATE, generate_audio, preload_models
        from scipy.io.wavfile import write as write_wav
    except ImportError:
        error("Bark non installé. Lance : pip install bark scipy")
    try:
        preload_models()
        audio    = generate_audio(texte, history_prompt=BARK_VOICES.get(langue, "v2/en_speaker_6"))
        wav_path = output_path.replace(".mp3", ".wav")
        write_wav(wav_path, SAMPLE_RATE, audio)
        os.system(f"ffmpeg -i {wav_path} -q:a 0 {output_path} -y -loglevel quiet")
        os.remove(wav_path)
        return True
    except Exception as e:
        warn(f"Bark échoué : {e}")
        return False

ELEVENLABS_VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "adam":   "pNInz6obpgDQGcFmaJgB",
}

def generer_elevenlabs(texte: str, voice_name: str, output_path: str) -> bool:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        error("ELEVENLABS_API_KEY non définie.")
    try:
        import requests
    except ImportError:
        error("requests non installé. Lance : pip install requests")
    voice_id = ELEVENLABS_VOICES.get(voice_name.lower(), ELEVENLABS_VOICES["rachel"])
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
            json={"text": texte, "model_id": "eleven_multilingual_v2",
                  "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
        )
        if r.status_code == 200:
            open(output_path, "wb").write(r.content)
            return True
        warn(f"ElevenLabs erreur {r.status_code}")
        return False
    except Exception as e:
        warn(f"ElevenLabs échoué : {e}")
        return False


# ─── Moteur TTS principal ────────────────────────────────────────────────────

class TTSEngine:
    def __init__(self, data: dict, output_dir: str):
        self.data        = data
        self.langue      = data["meta"].get("langue", "fr")
        self.personnages = data.get("personnages", {})
        self.cache       = load_cache()
        self.tts_dir     = os.path.join(output_dir, "tts")
        os.makedirs(self.tts_dir, exist_ok=True)

    def generate_all(self) -> dict:
        """Génère tous les fichiers TTS. Retourne un dict {scene_id_msg_idx: path}"""
        info("Démarrage génération TTS...")
        tts_map = {}
        total   = 0

        for scene in self.data.get("scenes", []):
            if scene.get("type") != "sms" or not scene.get("tts", False):
                continue
            for j, msg in enumerate(scene.get("messages", [])):
                texte = msg.get("texte")
                if not texte:
                    continue
                voix  = self.personnages.get(msg["perso"], {}).get("voix", "gtts")
                path  = os.path.join(self.tts_dir, f"scene{scene['id']}_msg{j}.mp3")
                if self._generer_un(texte, voix, path):
                    key = f"{scene['id']}_{j}"
                    tts_map[key] = path
                    total += 1

        save_cache(self.cache)
        success(f"{total} fichier(s) TTS générés")
        return tts_map

    def _generer_un(self, texte: str, voix: str, output_path: str) -> bool:
        key = cache_key(texte, self.langue, voix)
        if key in self.cache and os.path.exists(self.cache[key]):
            shutil.copy(self.cache[key], output_path)
            info(f"Cache : '{texte[:30]}'")
            return True

        info(f"TTS [{voix}] : '{texte[:40]}'")
        if voix == "gtts":
            ok = generer_gtts(texte, self.langue, output_path)
        elif voix == "bark":
            ok = generer_bark(texte, self.langue, output_path)
        elif voix.startswith("elevenlabs:"):
            ok = generer_elevenlabs(texte, voix.split(":")[1], output_path)
        else:
            warn(f"Voix '{voix}' inconnue → fallback gTTS")
            ok = generer_gtts(texte, self.langue, output_path)

        if ok:
            self.cache[key] = output_path
            success(f"✅ {os.path.basename(output_path)}")
        else:
            warn(f"❌ Échec : '{texte[:30]}'")
        return ok


if __name__ == "__main__":
    print(f"\n{BOLD}Test TTS Engine{RESET}\n")
    data_test = {
        "meta": {"langue": "fr"},
        "personnages": {"moi": {"voix": "gtts"}, "chef": {"voix": "gtts"}},
        "scenes": [{"id": 1, "type": "sms", "tts": True, "vitesse": 80, "messages": [
            {"perso": "moi",  "texte": "Chef j'ai fait une petite erreur"},
            {"perso": "chef", "texte": "C'est quoi encore"},
        ]}]
    }
    engine  = TTSEngine(data_test, output_dir="./test_output")
    tts_map = engine.generate_all()
    print(f"\nFichiers : {tts_map}")
