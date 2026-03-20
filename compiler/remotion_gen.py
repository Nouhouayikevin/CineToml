"""
CineToml Remotion Generator v1.0
Génère automatiquement le code React/Remotion depuis un fichier CineToml parsé
"""

import os
import sys
import json

GREEN = "\033[92m"
BLUE  = "\033[94m"
RESET = "\033[0m"
BOLD  = "\033[1m"

def success(msg): print(f"{GREEN}[REMOTION GEN OK]{RESET} {msg}")
def info(msg):    print(f"{BLUE}[REMOTION GEN]{RESET} {msg}")

RESOLUTIONS    = {"9x16": (1080, 1920), "16x9": (1920, 1080), "1x1": (1080, 1080)}
FPS_DEFAULT    = 30
FRAMES_PER_MSG = 80


class RemotionGenerator:
    def __init__(self, data: dict, remotion_dir: str, tts_map: dict = None):
        self.data         = data
        self.remotion_dir = remotion_dir
        self.tts_map      = tts_map or {}
        self.meta         = data["meta"]
        self.personnages  = data.get("personnages", {})
        self.bruitages    = data.get("bruitages", {})
        self.scenes       = data.get("scenes", [])
        self.interface    = data.get("interface", {})
        self.audio        = data.get("audio", {})
        w, h              = RESOLUTIONS.get(self.meta["resolution"], (1080, 1920))
        self.width        = w
        self.height       = h
        self.fps          = self.meta.get("fps", FPS_DEFAULT)
        self.total_frames = self._calc_total_frames()

    def _frames_scene(self, scene: dict) -> int:
        t = scene.get("type")
        if t in ("titre", "reaction", "outro", "focus"):
            return int(scene.get("duree", 3.0) * self.fps)
        if t == "sms":
            nb  = len(scene.get("messages", []))
            spd = scene.get("vitesse", FRAMES_PER_MSG)
            return nb * spd + self.fps * 2
        return self.fps * 2

    def _calc_total_frames(self) -> int:
        return sum(self._frames_scene(s) for s in self.scenes)

    def _resolve_bruitage(self, b: str) -> str:
        if not b:
            return None
        if b.startswith("$"):
            return self.bruitages.get(b[1:])
        return b

    def generate(self) -> int:
        info("Génération du code Remotion...")
        src = os.path.join(self.remotion_dir, "src")
        os.makedirs(src, exist_ok=True)
        self._write_root(src)
        self._write_composition(src)
        success(f"Code généré dans {src}")
        return self.total_frames

    def _write_root(self, src: str):
        content = f"""import {{Composition}} from 'remotion';
import {{CineTomlVideo}} from './Composition';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="CineTomlVideo"
    component={{CineTomlVideo}}
    durationInFrames={{{self.total_frames}}}
    fps={{{self.fps}}}
    width={{{self.width}}}
    height={{{self.height}}}
  />
);
"""
        with open(os.path.join(src, "Root.tsx"), "w") as f:
            f.write(content)
        success("Root.tsx écrit")

    def _write_composition(self, src: str):
        # Calcul des offsets
        offsets, cur = [], 0
        for s in self.scenes:
            offsets.append(cur)
            cur += self._frames_scene(s)

        scenes_json    = json.dumps(self.scenes,      ensure_ascii=False, indent=2)
        persos_json    = json.dumps(self.personnages, ensure_ascii=False, indent=2)
        bruitages_json = json.dumps(self.bruitages,   ensure_ascii=False, indent=2)
        interface_json = json.dumps(self.interface,   ensure_ascii=False, indent=2)
        audio_json     = json.dumps(self.audio,       ensure_ascii=False, indent=2)
        meta_json      = json.dumps(self.meta,        ensure_ascii=False, indent=2)
        offsets_json   = json.dumps(offsets)

        content = f"""import React from 'react';
import {{
  useCurrentFrame, useVideoConfig, interpolate, spring,
  Audio, Video, Img, Sequence, AbsoluteFill,
}} from 'remotion';

// ── Données CineToml (auto-générées) ──────────────────────────────────────
const SCENES      = {scenes_json};
const PERSONNAGES = {persos_json};
const BRUITAGES   = {bruitages_json};
const INTERFACE   = {interface_json};
const AUDIO_META  = {audio_json};
const META        = {meta_json};
const OFFSETS     = {offsets_json};
const FPS         = {self.fps};

// ── Bulle SMS ──────────────────────────────────────────────────────────────
const Bubble: React.FC<{{
  texte: string; couleur: string; cote: 'left'|'right';
  startFrame: number; effet?: string;
}}> = ({{ texte, couleur, cote, startFrame, effet }}) => {{
  const frame = useCurrentFrame();

  const progress = spring({{
    frame: frame - startFrame, fps: FPS,
    config: {{ damping: 14, stiffness: 200, mass: 0.8 }},
  }});

  const opacity = interpolate(frame - startFrame, [0, 6], [0, 1], {{
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  }});

  if (frame < startFrame) return null;
  const isRight = cote === 'right';

  const shakeX = effet === 'shake'
    ? Math.sin((frame - startFrame) * 2) *
      interpolate(frame - startFrame, [0, 15], [8, 0], {{ extrapolateRight: 'clamp' }})
    : 0;

  return (
    <div style={{{{
      display: 'flex',
      justifyContent: isRight ? 'flex-end' : 'flex-start',
      marginBottom: 18, opacity,
      transform: `scale(${{progress}}) translateX(${{shakeX}}px)`,
      transformOrigin: isRight ? 'bottom right' : 'bottom left',
      paddingLeft:  isRight ? 100 : 0,
      paddingRight: isRight ? 0   : 100,
    }}}}>
      <div style={{{{
        backgroundColor: couleur,
        borderRadius: 24, padding: '18px 28px', maxWidth: '78%',
        color: 'white', fontSize: 38,
        fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
        fontWeight: 500, lineHeight: 1.4,
        boxShadow: '0 2px 12px rgba(0,0,0,0.35)', wordBreak: 'break-word',
      }}}}>
        {{texte}}
      </div>
    </div>
  );
}};

// ── Header Téléphone ───────────────────────────────────────────────────────
const PhoneHeader: React.FC<{{ nom: string }}> = ({{ nom }}) => (
  <div style={{{{
    position: 'absolute', top: 0, left: 0, right: 0,
    padding: '20px 40px 16px',
    backgroundColor: 'rgba(0,0,0,0.85)',
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    zIndex: 100,
  }}}}>
    <span style={{{{ color: 'white', fontSize: 32, fontFamily: '-apple-system, sans-serif' }}}}>
      {{INTERFACE.heure ?? '14:32'}}
    </span>
    <span style={{{{ color: 'white', fontSize: 42, fontWeight: 700, fontFamily: '-apple-system, sans-serif' }}}}>
      {{nom}}
    </span>
    <span style={{{{ color: 'white', fontSize: 28, opacity: 0.8 }}}}>
      🔋 {{INTERFACE.batterie ?? 87}}%
    </span>
  </div>
);

// ── Scène TITRE ────────────────────────────────────────────────────────────
const SceneTitre: React.FC<{{ scene: any; offset: number }}> = ({{ scene, offset }}) => {{
  const frame  = useCurrentFrame();
  const localF = frame - offset;
  const dureeF = scene.duree * FPS;

  const opacity = interpolate(localF, [0, 20, dureeF - 20, dureeF], [0, 1, 1, 0], {{
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  }});
  const scale = spring({{ frame: localF, fps: FPS, config: {{ damping: 18, stiffness: 120 }} }});

  return (
    <AbsoluteFill style={{{{ backgroundColor: scene.fond ?? '#000', justifyContent: 'center', alignItems: 'center' }}}}>
      <div style={{{{
        opacity, transform: `scale(${{scale}})`,
        textAlign: 'center', padding: '0 60px',
        color: 'white', fontSize: scene.taille_texte ?? 72,
        fontFamily: '-apple-system, sans-serif',
        fontWeight: 800, lineHeight: 1.3,
      }}}}>
        {{scene.texte}}
      </div>
      {{META.watermark && (
        <div style={{{{
          position: 'absolute', bottom: 60,
          color: 'rgba(255,255,255,0.4)', fontSize: 32, fontFamily: '-apple-system, sans-serif',
        }}}}>
          {{META.watermark}}
        </div>
      )}}
    </AbsoluteFill>
  );
}};

// ── Scène SMS ──────────────────────────────────────────────────────────────
const SceneSMS: React.FC<{{ scene: any; offset: number }}> = ({{ scene, offset }}) => {{
  const frame   = useCurrentFrame();
  const localF  = frame - offset;
  const msgs    = scene.messages ?? [];
  const vitesse = scene.vitesse  ?? 80;

  const premierPerso = msgs[0]?.perso ?? '';
  const nomHeader    = PERSONNAGES[premierPerso]?.nom ?? premierPerso.toUpperCase();
  const visibles     = msgs.filter((_: any, i: number) => localF >= i * vitesse);
  const scrollY      = Math.max(0, (visibles.length - 5) * 115);

  return (
    <AbsoluteFill style={{{{ backgroundColor: '#000' }}}}>
      {{scene.fond_video && (
        <Video src={{scene.fond_video}}
          style={{{{ position:'absolute', inset:0, width:'100%', height:'100%',
            objectFit:'cover', opacity: scene.fond_opacite ?? 0.4 }}}} />
      )}}
      {{scene.fond_image && (
        <Img src={{scene.fond_image}}
          style={{{{ position:'absolute', inset:0, width:'100%', height:'100%',
            objectFit:'cover', opacity: scene.fond_opacite ?? 0.4 }}}} />
      )}}

      <PhoneHeader nom={{nomHeader}} />

      <div style={{{{
        position: 'absolute', top: 120, bottom: 40, left: 0, right: 0,
        padding: '20px 30px', display: 'flex',
        flexDirection: 'column', justifyContent: 'flex-end', overflow: 'hidden',
      }}}}>
        <div style={{{{ transform: `translateY(-${{scrollY}}px)` }}}}>
          {{msgs.map((msg: any, i: number) => {{
            const perso = PERSONNAGES[msg.perso] ?? {{}};
            if (!msg.texte) return null;
            return (
              <Bubble
                key={{i}}
                texte={{msg.texte}}
                couleur={{msg.couleur ?? perso.couleur ?? '#3C3C3E'}}
                cote={{perso.cote ?? 'left'}}
                startFrame={{offset + i * vitesse}}
                effet={{msg.effet}}
              />
            );
          }})}}
        </div>
      </div>

      {{META.watermark && (
        <div style={{{{
          position: 'absolute', bottom: 20, right: 30,
          color: 'rgba(255,255,255,0.3)', fontSize: 26, fontFamily: '-apple-system, sans-serif',
        }}}}>
          {{META.watermark}}
        </div>
      )}}
    </AbsoluteFill>
  );
}};

// ── Scène REACTION ─────────────────────────────────────────────────────────
const SceneReaction: React.FC<{{ scene: any; offset: number }}> = ({{ scene, offset }}) => {{
  const frame  = useCurrentFrame();
  const localF = frame - offset;
  const dureeF = scene.duree * FPS;

  const opacity = interpolate(localF, [0, 8, dureeF - 8, dureeF], [0, 1, 1, 0], {{
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  }});
  const scale = scene.effet === 'zoom_in'
    ? interpolate(localF, [0, dureeF], [1, 1.15], {{ extrapolateRight: 'clamp' }})
    : scene.effet === 'zoom_out'
    ? interpolate(localF, [0, dureeF], [1.15, 1], {{ extrapolateRight: 'clamp' }})
    : 1;
  const shakeX = scene.effet === 'shake'
    ? Math.sin(localF * 3) * interpolate(localF, [0, 20], [10, 0], {{ extrapolateRight: 'clamp' }})
    : 0;

  const ext     = scene.media?.split('.').pop()?.toLowerCase();
  const isVideo = ['mp4', 'mov', 'webm'].includes(ext);

  return (
    <AbsoluteFill style={{{{ backgroundColor: '#000', overflow: 'hidden' }}}}>
      <div style={{{{ width:'100%', height:'100%', opacity, transform:`scale(${{scale}}) translateX(${{shakeX}}px)` }}}}>
        {{isVideo
          ? <Video src={{scene.media}} style={{{{ width:'100%', height:'100%', objectFit:'cover' }}}} />
          : <Img   src={{scene.media}} style={{{{ width:'100%', height:'100%', objectFit:'cover' }}}} />
        }}
      </div>
      {{scene.texte_overlay && (
        <div style={{{{
          position:'absolute', bottom:120, left:0, right:0,
          textAlign:'center', fontSize:80,
        }}}}>
          {{scene.texte_overlay}}
        </div>
      )}}
    </AbsoluteFill>
  );
}};

// ── Scène OUTRO ────────────────────────────────────────────────────────────
const SceneOutro: React.FC<{{ scene: any; offset: number }}> = ({{ scene, offset }}) => {{
  const frame  = useCurrentFrame();
  const localF = frame - offset;
  const dureeF = scene.duree * FPS;

  const opacity = interpolate(localF, [0, 20, dureeF - 20, dureeF], [0, 1, 1, 0], {{
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  }});

  return (
    <AbsoluteFill style={{{{ backgroundColor: '#000', justifyContent:'center', alignItems:'center' }}}}>
      <div style={{{{
        opacity, color:'white', fontSize:64, fontWeight:700,
        fontFamily:'-apple-system, sans-serif', textAlign:'center', padding:'0 60px',
      }}}}>
        {{scene.texte}}
      </div>
    </AbsoluteFill>
  );
}};

// ── Composant Principal ────────────────────────────────────────────────────
export const CineTomlVideo: React.FC = () => (
  <AbsoluteFill style={{{{ backgroundColor: '#000' }}}}>

    {{AUDIO_META.musique && (
      <Audio src={{AUDIO_META.musique}} volume={{AUDIO_META.volume ?? 0.3}} startFrom={{0}} />
    )}}

    {{SCENES.map((scene: any, i: number) => {{
      const offset = OFFSETS[i];
      const dureeF = (() => {{
        const t = scene.type;
        if (t === 'sms') return scene.messages.length * (scene.vitesse ?? 80) + FPS * 2;
        return Math.round((scene.duree ?? 3) * FPS);
      }})();

      return (
        <Sequence key={{i}} from={{offset}} durationInFrames={{dureeF}}>
          {{scene.type === 'titre'    && <SceneTitre    scene={{scene}} offset={{offset}} />}}
          {{scene.type === 'sms'      && <SceneSMS      scene={{scene}} offset={{offset}} />}}
          {{scene.type === 'reaction' && <SceneReaction scene={{scene}} offset={{offset}} />}}
          {{scene.type === 'outro'    && <SceneOutro    scene={{scene}} offset={{offset}} />}}
        </Sequence>
      );
    }})}}
  </AbsoluteFill>
);
"""
        with open(os.path.join(src, "Composition.tsx"), "w") as f:
            f.write(content)
        success("Composition.tsx écrit")


# ─── Standalone ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    from parser import CineTomlParser

    if len(sys.argv) < 3:
        print("Usage: python remotion_gen.py <fichier.toml> <remotion_dir>")
        sys.exit(1)

    data = CineTomlParser(sys.argv[1]).load()
    gen  = RemotionGenerator(data, sys.argv[2])
    gen.generate()
