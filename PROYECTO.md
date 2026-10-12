# ChaskiBoom Battle Chess — notas del proyecto

Documento de trabajo para retomar el desarrollo (también sirve de contexto para Claude).

## Qué es

Ajedrez web de Daniel Camargo, inspirado en el Battle Chess de su infancia: cuando una pieza captura a otra,
pelean una batalla corta en 3D. Tiene vista 2D clásica, CPU con niveles y modo online entre amigos.

- Sitio: https://danieltdfdev.github.io/BattleChess/ (GitHub Pages, rama `main`, raíz)
- Copia de pruebas: https://danieltdfdev.github.io/BattleChess/dev/
- Versión actual: ver `<span id="ver">` en `src/game_template.html`

## Estructura del repo

| Ruta | Qué es |
|---|---|
| `src/game_template.html` | **Código fuente del juego. Se edita acá.** Tiene marcadores `__ASSETS__`, `__PIECES__`, `__SOUNDS__`, `__LOGO__`, `__ENGINE__`, `__FIREBASE__` |
| `tools/build.py` | Genera `index.html`, `dev/index.html` o `build/artifact.html` a partir del template |
| `index.html` | Página principal (generada, no editar a mano) |
| `dev/index.html` | Copia de pruebas (generada) |
| `assets/models`, `assets/anims` | Personajes, armas y animaciones KayKit (.glb) |
| `assets/pieces/<juego>/` | Piezas 2D en SVG (cburnett, merida, chessnut, celtic, fantasy) |
| `assets/sounds/` | Sonidos convertidos a MP3 mono (los originales de Daniel están en `/sonidos`) |
| `assets/engine/` | Stockfish 18 lite (Stockfish.js, GPLv3) + licencia |
| `assets/logo.webp` | Logo con transparencia real (recortado de `logo_chaskiboom.jpg`) |
| `src/sw.js` | Service worker (la build lo copia como `sw.js` junto a cada página, con la versión en el nombre de la caché) |
| `assets/icons/` | Íconos de la app generados desde `assets/icono_chaskiboom.png` (favicon, apple-touch-icon, 192/512 normales y maskable) |
| `database.rules.json` | Reglas de seguridad de Firebase Realtime Database (se pegan en la consola) |

## Forma de trabajo

1. Se itera viendo el juego como artifact en el chat (`python tools/build.py artifact` → `build/artifact.html`).
   El artifact no puede conectarse a internet: no tiene Firebase ni Stockfish (usa el motor propio de respaldo).
2. Los cambios se suben a `/dev/` (`python tools/build.py dev`) para probar en el celular y el online.
3. Cuando Daniel dice **"publicar"**: subir la versión en el template (v1.4 → v1.5…; v2.0 para saltos grandes),
   regenerar `index.html` y `dev/index.html`, probar, y commitear con el número de versión en el mensaje.
4. El repo principal no se toca hasta que Daniel lo indica.

## Decisiones tomadas

- **Motor:** Three.js r147 (UMD por CDN), chess.js 0.10.3. Sin herramientas de compilación.
- **Personajes (KayKit Adventurers 2.0 + Character Animations 1.1, CC0):** peón = pícaro con daga,
  caballo = caballero con espada y escudo, alfil = maga con bastón, torre = bárbaro con hacha a dos manos,
  dama = maga con varita y corona (sin sombrero), rey = caballero con corona (sin casco).
- **Bandos:** azules (blancas) y rojos (negras), recoloreando la ropa en la textura; gorro de oso de la torre
  recoloreado entero; base redonda del color del bando. En 2D: blanco y negro clásico.
- **Peleas:** tres tiempos (golpe, contraataque, remate), impacto calculado por la velocidad de la mano del arma,
  cámara lateral, piezas vecinas translúcidas, la capturada se hunde en el tablero.
- **Sonidos:** de batalla solo en peleas 3D; espadas/hachas/armaduras/quejidos al azar sin repetir;
  quejidos femeninos para dama, peón y alfil; magia para dama y alfil; enroque, jaque, ganador/perdedor.
- **CPU:** Stockfish 18 lite en Web Worker, 5 niveles (Muy fácil … Experto) elegidos en el cartel de nueva partida.
- **Online (Firebase, proyecto `battlechess-d51bf`):** autenticación anónima con vinculación opcional a Google,
  Realtime Database `games/<código>` y `users/<uid>/games`; desafío por link `#código`, sorteo de colores,
  las blancas tocan Comenzar, jugadas en cola reproducidas con animación, tablas, abandono, revancha,
  correspondencia («Mis partidas»), chat con 20 frases para el rival (cartel 1 s, una cada 15 s).
- **Instalable como app (PWA):** la build genera `manifest.webmanifest` y `sw.js` al lado de `index.html` y de `dev/index.html`
  (la de dev se instala aparte, como «ChaskiBoom dev»). El service worker es *red primero*: siempre baja lo último y usa la caché
  solo sin conexión; no toca Firebase ni pedidos de audio por rangos. El artifact no lleva nada de esto (marcador `__PWA__` vacío).
- **Diseño:** tipografías Cinzel + EB Garamond; en PC columna lateral con logo y consola; en celular,
  consola plegable (historial + Menú).

## Pendientes / ideas

- **Probar la instalación como app (v1.7, ya en producción):** Android (Chrome → Instalar app) e iPhone (Safari → Compartir → Agregar a inicio).
  Revisar ícono, pantalla completa, desafío por link y online. En iPhone la app instalada no comparte sesión con Safari:
  el usuario anónimo es otro, así que «Mis partidas» solo se conserva vinculando Google.

- Partidas con tiempo límite (los relojes ya existen).
- Calibrar los niveles de la CPU con partidas reales.
- Logo nuevo con la "E" de BATTLE completa, exportado como PNG transparente.
- Depurar el online con jugadores reales.
