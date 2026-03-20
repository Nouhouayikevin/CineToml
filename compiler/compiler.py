"""
CineToml Compiler Engine v1.0
Lance le rendu final via Remotion + FFmpeg
"""

import os
import sys
import subprocess
import shutil
import time

RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def error(msg):   print(f"{RED}{BOLD}[COMPILER ERREUR]{RESET} {msg}"); sys.exit(1)
def warn(msg):    print(f"{YELLOW}[COMPILER WARN]{RESET} {msg}")
def success(msg): print(f"{GREEN}[COMPILER OK]{RESET} {msg}")
def info(msg):    print(f"{BLUE}[COMPILER INFO]{RESET} {msg}")


class RenderEngine:
    def __init__(self, remotion_dir: str, output_file: str, composition_id: str = "CineTomlVideo"):
        self.remotion_dir    = remotion_dir
        self.output_file     = output_file
        self.composition_id  = composition_id

        # Vérifications préalables
        self._check_dependencies()
        self._check_remotion_dir()

    # ── Vérifications ────────────────────────
    def _check_dependencies(self):
        """Vérifie que Node.js, npm et ffmpeg sont installés"""
        for tool in ["node", "npm", "ffmpeg"]:
            if not shutil.which(tool):
                error(f"'{tool}' non trouvé. Installe-le avant de continuer.")
        success("Dépendances système OK (node, npm, ffmpeg)")

    def _check_remotion_dir(self):
        """Vérifie que le projet Remotion est valide"""
        if not os.path.exists(self.remotion_dir):
            error(f"Dossier Remotion introuvable : {self.remotion_dir}")

        package_json = os.path.join(self.remotion_dir, "package.json")
        if not os.path.exists(package_json):
            error(f"package.json introuvable dans {self.remotion_dir}")

        # Installer node_modules si absent
        node_modules = os.path.join(self.remotion_dir, "node_modules")
        if not os.path.exists(node_modules):
            info("node_modules absent — installation en cours...")
            self._run(["npm", "install"], cwd=self.remotion_dir, timeout=120)
            success("npm install terminé")

    # ── Rendu principal ──────────────────────
    def render(self, total_frames: int, fps: int) -> str:
        """Lance le rendu Remotion et retourne le path du fichier MP4"""
        duree = total_frames / fps
        info(f"Rendu : {total_frames} frames @ {fps}fps = {duree:.1f}s")
        info(f"Sortie : {self.output_file}")

        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        start = time.time()

        result = subprocess.run(
            [
                "npx", "remotion", "render",
                self.composition_id,
                self.output_file,
                "--log", "verbose",
                "--concurrency", "4",
            ],
            cwd=self.remotion_dir,
            text=True,
            timeout=600,  # 10 minutes max
        )

        if result.returncode != 0:
            error(f"Remotion render échoué (code {result.returncode})")

        if not os.path.exists(self.output_file):
            error(f"Fichier de sortie non créé : {self.output_file}")

        elapsed  = time.time() - start
        size_mb  = os.path.getsize(self.output_file) / (1024 * 1024)

        success(f"✅ Vidéo rendue en {elapsed:.1f}s — {size_mb:.1f} MB")
        success(f"📁 {self.output_file}")

        return self.output_file

    # ── Post-traitement optionnel ────────────
    def optimize(self, input_path: str) -> str:
        """
        Optimise la vidéo avec FFmpeg pour les réseaux sociaux
        — Réduit la taille sans perte de qualité visible
        — Compatible Instagram, TikTok, YouTube Shorts
        """
        output_path = input_path.replace(".mp4", "_optimized.mp4")
        info(f"Optimisation FFmpeg en cours...")

        result = subprocess.run(
            [
                "ffmpeg",
                "-i", input_path,
                "-vcodec", "libx264",
                "-crf", "23",           # qualité (18=haute, 28=basse)
                "-preset", "fast",
                "-acodec", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",  # streaming optimisé
                "-y",                   # overwrite
                output_path
            ],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            warn(f"Optimisation échouée : {result.stderr[:200]}")
            return input_path  # retourner l'original si échec

        orig_mb = os.path.getsize(input_path) / (1024 * 1024)
        opt_mb  = os.path.getsize(output_path) / (1024 * 1024)
        saved   = ((orig_mb - opt_mb) / orig_mb) * 100

        success(f"Optimisation : {orig_mb:.1f}MB → {opt_mb:.1f}MB ({saved:.0f}% économisé)")
        return output_path

    # ── Helper subprocess ────────────────────
    def _run(self, cmd: list, cwd: str = None, timeout: int = 60):
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            error(f"Commande échouée : {' '.join(cmd)}\n{result.stderr}")
        return result


# ─── Standalone ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compiler.py <remotion_dir> <output.mp4>")
        sys.exit(1)

    engine = RenderEngine(
        remotion_dir=sys.argv[1],
        output_file=sys.argv[2],
    )
    engine.render(total_frames=900, fps=30)
