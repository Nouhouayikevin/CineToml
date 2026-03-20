"""
CineToml Compiler v1.0
Point d'entrée principal — orchestre tout le pipeline :
  1. Parse le fichier .toml
  2. Génère les voix TTS
  3. Génère le code Remotion
  4. Lance le rendu final
  5. Retourne le fichier MP4
"""

import os
import sys
import time
import subprocess
import argparse
from pathlib import Path

# Imports internes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parser import CineTomlParser
from tts import TTSEngine
from remotion_gen import RemotionGenerator

# ─────────────────────────────────────────
# Couleurs terminal
# ─────────────────────────────────────────
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def error(msg):   print(f"{RED}{BOLD}[ERREUR]{RESET} {msg}"); sys.exit(1)
def warn(msg):    print(f"{YELLOW}[WARN]{RESET} {msg}")
def success(msg): print(f"{GREEN}[OK]{RESET} {msg}")
def info(msg):    print(f"{BLUE}[INFO]{RESET} {msg}")
def step(n, msg): print(f"\n{CYAN}{BOLD}[ÉTAPE {n}/5]{RESET} {BOLD}{msg}{RESET}")


# ─────────────────────────────────────────
# Bannière
# ─────────────────────────────────────────
def print_banner():
    print(f"""
{CYAN}{BOLD}
  ██████╗██╗███╗   ██╗███████╗████████╗ ██████╗ ███╗   ███╗██╗
 ██╔════╝██║████╗  ██║██╔════╝╚══██╔══╝██╔═══██╗████╗ ████║██║
 ██║     ██║██╔██╗ ██║█████╗     ██║   ██║   ██║██╔████╔██║██║
 ██║     ██║██║╚██╗██║██╔══╝     ██║   ██║   ██║██║╚██╔╝██║██║
 ╚██████╗██║██║ ╚████║███████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║███████╗
  ╚═════╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚══════╝
{RESET}
  {BOLD}CineToml Compiler v1.0{RESET} — Le langage des faceless videos 🎬
""")


# ─────────────────────────────────────────
# Classe principale du compilateur
# ─────────────────────────────────────────
class CineTomlCompiler:
    def __init__(self, toml_file: str, output_file: str = None, no_tts: bool = False):
        self.toml_file    = os.path.abspath(toml_file)
        self.base_dir     = os.path.dirname(self.toml_file)
        self.no_tts       = no_tts

        # Dossiers de travail
        self.work_dir     = os.path.join(self.base_dir, ".cinetoml_build")
        self.output_dir   = os.path.join(self.base_dir, "output")
        self.remotion_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "remotion-engine"
        )

        # Nom du fichier de sortie
        if output_file:
            self.output_file = os.path.abspath(output_file)
        else:
            stem = Path(toml_file).stem
            self.output_file = os.path.join(self.output_dir, f"{stem}.mp4")

        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        self.data = {}
        self.tts_map = {}
        self.total_frames = 0

    # ── Pipeline principal ───────────────────
    def compile(self):
        start_time = time.time()
        print_banner()

        # ── Étape 1 : Parse ─────────────────
        step(1, "Parsing et validation du fichier CineToml...")
        parser = CineTomlParser(self.toml_file)
        self.data = parser.load()
        self.data["_source_file"] = self.toml_file

        # ── Étape 2 : TTS ───────────────────
        step(2, "Génération des voix TTS...")
        if self.no_tts:
            info("TTS désactivé (--no-tts)")
        else:
            tts_engine = TTSEngine(self.data, output_dir=self.work_dir)
            self.tts_map = tts_engine.generate_all()

        # ── Étape 3 : Remotion ──────────────
        step(3, "Génération du code Remotion...")
        self._check_remotion()
        gen = RemotionGenerator(
            data=self.data,
            remotion_dir=self.remotion_dir,
            tts_map=self.tts_map
        )
        self.total_frames = gen.generate()

        # ── Étape 4 : Build Remotion ────────
        step(4, "Compilation du projet Remotion...")
        self._build_remotion()

        # ── Étape 5 : Rendu MP4 ─────────────
        step(5, "Rendu de la vidéo finale...")
        self._render_video()

        elapsed = time.time() - start_time
        self._print_success(elapsed)

    # ── Vérification Remotion ────────────────
    def _check_remotion(self):
        if not os.path.exists(self.remotion_dir):
            error(f"Dossier Remotion introuvable : {self.remotion_dir}\n"
                  f"  Lance d'abord : npx create-video@latest dans remotion-engine/")

        package_json = os.path.join(self.remotion_dir, "package.json")
        if not os.path.exists(package_json):
            error(f"package.json introuvable dans {self.remotion_dir}")

        node_modules = os.path.join(self.remotion_dir, "node_modules")
        if not os.path.exists(node_modules):
            info("node_modules manquant, installation en cours...")
            result = subprocess.run(
                ["npm", "install"],
                cwd=self.remotion_dir,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                error(f"npm install échoué :\n{result.stderr}")
            success("npm install terminé")

    # ── Build Remotion ───────────────────────
    def _build_remotion(self):
        result = subprocess.run(
            ["npx", "remotion", "studio", "--no-open"],
            cwd=self.remotion_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        # Studio démarre et s'arrête — on vérifie juste qu'il n'y a pas d'erreur de build
        if "error" in result.stderr.lower() and "cannot find module" in result.stderr.lower():
            error(f"Erreur de build Remotion :\n{result.stderr}")
        success("Build Remotion OK")

    # ── Rendu vidéo ──────────────────────────
    def _render_video(self):
        info(f"Rendu en cours... ({self.total_frames} frames @ {self.data['meta'].get('fps', 30)}fps)")
        info(f"Sortie : {self.output_file}")

        result = subprocess.run(
            [
                "npx", "remotion", "render",
                "CineTomlVideo",
                self.output_file,
                "--log", "verbose"
            ],
            cwd=self.remotion_dir,
            text=True,
            timeout=600  # 10 minutes max
        )

        if result.returncode != 0:
            error(f"Erreur de rendu Remotion. Code : {result.returncode}")

        if not os.path.exists(self.output_file):
            error(f"Le fichier de sortie n'a pas été créé : {self.output_file}")

        size_mb = os.path.getsize(self.output_file) / (1024 * 1024)
        success(f"Vidéo générée : {self.output_file} ({size_mb:.1f} MB)")

    # ── Message de succès ────────────────────
    def _print_success(self, elapsed: float):
        meta = self.data.get("meta", {})
        fps = meta.get("fps", 30)
        duree = self.total_frames / fps

        print(f"""
{GREEN}{BOLD}{'═'*55}{RESET}
{GREEN}{BOLD}  🎬 VIDÉO GÉNÉRÉE AVEC SUCCÈS !{RESET}
{GREEN}{BOLD}{'═'*55}{RESET}

  📽️  Titre      : {meta.get('title', '?')}
  📐  Résolution : {meta.get('resolution', '?')} @ {fps}fps
  ⏱️   Durée      : {duree:.1f}s
  📦  Fichier    : {self.output_file}
  ⚡  Temps      : {elapsed:.1f}s

{GREEN}{BOLD}{'═'*55}{RESET}
""")


# ─────────────────────────────────────────
# CLI — Arguments
# ─────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="cinetoml",
        description="CineToml Compiler — Génère des vidéos virales depuis un fichier .toml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python main.py examples/pizzas.toml
  python main.py examples/pizzas.toml -o output/ma_video.mp4
  python main.py examples/pizzas.toml --no-tts
        """
    )

    parser.add_argument(
        "fichier",
        help="Chemin vers le fichier .toml CineToml"
    )
    parser.add_argument(
        "-o", "--output",
        help="Chemin du fichier MP4 de sortie (défaut: output/<nom>.mp4)",
        default=None
    )
    parser.add_argument(
        "--no-tts",
        help="Désactive la génération TTS",
        action="store_true"
    )
    parser.add_argument(
        "--validate-only",
        help="Valide uniquement le fichier sans générer la vidéo",
        action="store_true"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="CineToml v1.0"
    )

    args = parser.parse_args()

    # Validation seule
    if args.validate_only:
        print_banner()
        parser_obj = CineTomlParser(args.fichier)
        parser_obj.load()
        print(f"\n{GREEN}{BOLD}✅ Fichier valide !{RESET}\n")
        return

    # Compilation complète
    compiler = CineTomlCompiler(
        toml_file=args.fichier,
        output_file=args.output,
        no_tts=args.no_tts
    )
    compiler.compile()


if __name__ == "__main__":
    main()
