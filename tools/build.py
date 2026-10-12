#!/usr/bin/env python3
"""
Genera el juego a partir de src/game_template.html y los recursos de assets/.

  python tools/build.py          -> index.html (página principal)
  python tools/build.py dev      -> dev/index.html (copia de pruebas)
  python tools/build.py artifact -> build/artifact.html (un solo archivo con todo embebido, sin Stockfish ni Firebase)

El código del juego se edita SOLO en src/game_template.html; index.html y dev/index.html se regeneran.
"""
import base64, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

MODELS = ['Rogue', 'Knight', 'Mage', 'Barbarian', 'sword_1handed', 'shield_badge_color', 'dagger', 'staff', 'wand', 'axe_2handed']
ANIMS = ['General', 'MovementBasic', 'MovementAdvanced', 'CombatMelee', 'CombatRanged', 'Simulation']
PIECE_SETS = ['cburnett', 'merida', 'chessnut', 'celtic', 'fantasy']
FIREBASE = '\n'.join('<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-%s-compat.js"></script>' % m for m in ('app', 'auth', 'database'))

def b64(path):
    return base64.b64encode(open(path, 'rb').read()).decode()

def assets_map():
    m = {k: 'assets/models/%s.glb' % k for k in MODELS}
    m.update({'anim_' + n: 'assets/anims/%s.glb' % n for n in ANIMS})
    return m

def pieces_map():
    return {s: {c + t.lower(): 'assets/pieces/%s/%s%s.svg' % (s, c, t) for c in 'wb' for t in 'KQRBNP'} for s in PIECE_SETS}

def sounds_map():
    return {os.path.splitext(f)[0]: 'assets/sounds/' + f for f in sorted(os.listdir('assets/sounds')) if f.endswith('.mp3')}

def page(t):
    """Envuelve el contenido del template en un documento HTML completo."""
    t = t.replace('<style>', '<style>\n  *, *::before, *::after { box-sizing: border-box; }\n  body { margin: 0; }\n  [hidden] { display: none !important; }', 1)
    t = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
         '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + t)
    i = t.index('<div id="stage">')
    return t[:i] + '</head>\n<body>\n' + t[i:] + '\n</body>\n</html>\n'

def build_site(dev):
    t = open('src/game_template.html', encoding='utf-8').read()
    t = (t.replace('__LOGO__', 'assets/logo.webp')
          .replace('__ASSETS__', json.dumps(assets_map(), indent=2))
          .replace('__PIECES__', json.dumps(pieces_map(), indent=2))
          .replace('__SOUNDS__', json.dumps(sounds_map(), indent=2))
          .replace('__ENGINE__', 'assets/engine/stockfish-18-lite-single.js')
          .replace('__FIREBASE__', FIREBASE))
    old = "  const parse = b64 => new Promise((res, rej) => loader.parse(toBuffer(b64), '', res, rej));"
    assert old in t
    t = t.replace(old, "  const parse = url => new Promise((res, rej) => loader.load(url, res, undefined, rej));   // cada modelo es un archivo .glb del repo")
    t = page(t)
    if dev:
        t = t.replace('"assets/', '"../assets/').replace("'assets/engine/", "'../assets/engine/")
        os.makedirs('dev', exist_ok=True)
        out = 'dev/index.html'
    else:
        out = 'index.html'
    open(out, 'w', encoding='utf-8').write(t)
    print('generado', out)

def build_artifact():
    t = open('src/game_template.html', encoding='utf-8').read()
    assets = {k: b64(v) for k, v in assets_map().items()}
    pieces = {s: {k: 'data:image/svg+xml;base64,' + b64(v) for k, v in m.items()} for s, m in pieces_map().items()}
    sounds = {k: 'data:audio/mpeg;base64,' + b64(v) for k, v in sounds_map().items()}
    t = (t.replace('__ENGINE__', '').replace('__FIREBASE__', '')
          .replace('__LOGO__', 'data:image/webp;base64,' + b64('assets/logo.webp'))
          .replace('__ASSETS__', json.dumps(assets)).replace('__PIECES__', json.dumps(pieces)).replace('__SOUNDS__', json.dumps(sounds)))
    os.makedirs('build', exist_ok=True)
    open('build/artifact.html', 'w', encoding='utf-8').write(t)
    print('generado build/artifact.html')

if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else ''
    if arg == 'artifact':
        build_artifact()
    else:
        build_site(arg == 'dev')
