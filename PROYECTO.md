# ChaskiBoom Battle Chess — notas del proyecto

Documento de trabajo para retomar el desarrollo (también sirve de contexto para Claude).

## Qué es

Ajedrez web de Daniel Camargo, inspirado en el Battle Chess de su infancia: cuando una pieza captura a otra,
pelean una batalla corta en 3D. Tiene vista 2D clásica, CPU con niveles y modo online entre amigos.

- Sitio: https://danieltdfdev.github.io/BattleChess/ (GitHub Pages, rama `main`, raíz)
- Copia de pruebas: https://danieltdfdev.github.io/BattleChess/dev/
- Repo: https://github.com/DanielTDFdev/BattleChess (se movió desde `danieltdfdev/battlechess`; usar esta URL como remoto)
- Versión actual: **v1.27** (ver `<span id="ver">` en `src/game_template.html`)

## Estructura del repo

| Ruta | Qué es |
|---|---|
| `src/game_template.html` | **Código fuente del juego. Se edita acá.** Tiene marcadores `__ASSETS__`, `__PIECES__`, `__SOUNDS__`, `__LOGO__`, `__ENGINE__`, `__FIREBASE__`, `__PWA__` |
| `src/sw.js` | Service worker (la build lo copia como `sw.js` junto a cada página, con la versión en el nombre de la caché) |
| `tools/build.py` | Genera `index.html`, `dev/index.html` o `build/artifact.html` a partir del template (más `manifest.webmanifest` y `sw.js` en raíz y dev) |
| `index.html` | Página principal (generada, no editar a mano) |
| `dev/index.html` | Copia de pruebas (generada) |
| `assets/models`, `assets/anims` | Personajes, armas y animaciones KayKit (.glb) |
| `assets/pieces/<juego>/` | Piezas 2D en SVG: 25 juegos de lichess (desde v1.13 se sumaron 20 a cburnett, merida, chessnut, celtic y fantasy). Autores y licencias en `assets/pieces/LICENCIAS.md`. La lista está en `PIECE_SETS` de `tools/build.py` y en el `<select id="pset">` del template |
| `assets/sounds/` | Sonidos convertidos a MP3 mono (los originales de Daniel están en `/sonidos`) |
| `assets/engine/` | Stockfish 18 lite (Stockfish.js, GPLv3) + licencia |
| `assets/logo.webp` | Logo con transparencia real (recortado de `logo_chaskiboom.jpg`) |
| `assets/winner.webp`, `assets/loser.webp` | Retratos de los carteles de ganador y perdedor (recortados de `winner.png` / `loser.png`, fondo transparente, 480 px de alto). Marcadores `__WINNER__` / `__LOSER__` |
| `assets/icono_chaskiboom.png` | Ícono original de la app (fondo blanco) |
| `assets/icons/` | Íconos generados desde `icono_chaskiboom.png`: favicon, apple-touch-icon, 192/512 normales y maskable |
| `database.rules.json` | Reglas de seguridad de Firebase Realtime Database (se pegan en la consola) |

## Forma de trabajo

1. Se itera viendo el juego como artifact en el chat (`python tools/build.py artifact` → `build/artifact.html`).
   El artifact no puede conectarse a internet: no tiene Firebase ni Stockfish (usa el motor propio de respaldo).
2. Los cambios se suben a `/dev/` (`python tools/build.py dev`) para probar en el celular y el online.
3. Cuando Daniel dice **"publicar"** (o "subilo a producción"): subir la versión en el template (v1.27 → v1.28…; v2.0 para saltos grandes),
   regenerar `index.html` y `dev/index.html`, probar, y commitear con el número de versión en el mensaje.
4. El repo principal no se toca hasta que Daniel lo indica.
5. Pruebas automáticas en la nube: el entorno bloquea las CDN (jsdelivr, Google Fonts). Para levantar el juego con
   Playwright hay que instalar `three@0.147.0` y `chess.js@0.10.3` con npm y servirlos con `page.route`. Es lento
   (la CPU y las animaciones bloquean con `busy`); para cambios chicos alcanza con `node --check` del script generado.
   El servidor local tiene que mandar `image/svg+xml` para los SVG, si no las piezas 2D no se ven.

## Decisiones tomadas

- **Motor:** Three.js r147 (UMD por CDN), chess.js 0.10.3. Sin herramientas de compilación.
- **Personajes (KayKit Adventurers 2.0 + Character Animations 1.1, CC0):** peón = pícaro con daga,
  caballo = caballero con espada y escudo, alfil = maga con bastón, torre = bárbaro con hacha a dos manos,
  dama = maga con varita y corona (sin sombrero), rey = caballero con corona (sin casco).
- **Bandos:** azules (blancas) y rojos (negras), recoloreando la ropa en la textura; gorro de oso de la torre
  recoloreado entero; base redonda del color del bando. En 2D: blanco y negro clásico.
- **Vista inicial (v1.7):** el juego arranca en 2D (`setView(true)` en el arranque, después de cargar los modelos);
  el botón «Vista 3D» pasa a las peleas. No se recuerda la última vista elegida.
- **Peleas:** tres tiempos (golpe, contraataque, remate), impacto calculado por la velocidad de la mano del arma,
  cámara lateral, piezas vecinas translúcidas, la capturada se hunde en el tablero.
- **Sonidos:** de batalla solo en peleas 3D; espadas/hachas/armaduras/quejidos al azar sin repetir;
  quejidos femeninos para dama, peón y alfil; magia para dama y alfil; enroque, jaque, ganador/perdedor.
  Al apoyar la pieza: `move_w`/`move_b`, o `come` si capturó. El enroque suena al arrancar (`castleSfx`), no al apoyar.
- **CPU:** Stockfish 18 lite en Web Worker, 5 niveles (Muy fácil … Experto) elegidos en el cartel de nueva partida.
  Stockfish en Skill Level 0 sigue siendo demasiado fuerte para principiantes, así que (desde v1.12) Muy fácil no usa
  Stockfish: 50 % jugadas al azar y 50 % `pickCpu` (come lo que ve, no deja piezas colgadas a 1 jugada). Fácil: 20 % al azar
  y el resto Stockfish nivel 0 a profundidad 1. Medio, Difícil y Experto sin cambios. En simulación, Muy fácil pierde
  37 de 40 contra un jugador que solo come piezas libres y no deja las suyas colgadas.
- **Nueva partida (v1.6):** el cartel tiene Comenzar y Cancelar. `drawColors(onCancel)` solo sortea y muestra el cartel;
  el tablero se reinicia recién en Comenzar (`resetGame(col)`). Cancelar deja la partida anterior intacta
  (y restaura el nivel de CPU si se cambió en el cartel); si no había partida empezada, vuelve a `chooseMode()`.
- **Online (Firebase, proyecto `battlechess-d51bf`):** autenticación anónima con vinculación opcional a Google,
  Realtime Database `games/<código>` y `users/<uid>/games`; desafío por link `#código`, sorteo de colores,
  las blancas tocan Comenzar, jugadas en cola reproducidas con animación, tablas, abandono, revancha,
  correspondencia («Mis partidas»), chat con 20 frases para el rival (cartel 3 s desde v1.5, una cada 15 s).
- **Avisos online sin servidor (v1.8):** no hay notificaciones push (se descartó por complejo).
  - Partida abierta: si la novedad llega con la página oculta, cambia el título y suena. Si llega hasta 20 s después de volver
    (en el celular llega al reconectarse Firebase), cartel de 5 s, sonido y vibración (`news()` / `showNews()`).
  - Otras partidas: un vigía (`watchAll` / `syncWatch`) escucha las 15 más recientes de `users/<uid>/games`
    que no están abiertas ni terminadas, y muestra un aviso arriba (`#other`) con «Ver partida».
    Hay que usar `off('value', cb)` para no cortar la escucha de la partida abierta. Si el jugador ya tiene apodo,
    Firebase se conecta al arrancar para vigilar aunque juegue contra la CPU. `fbInit()` es una sola promesa
    compartida, para no crear dos usuarios anónimos.
  - Para probar sin Firebase real: mock en memoria de la API compat servido con `page.route` (`window.firebase` falso con `ref/on/off/once/set/update/transaction`).
- **Instalable como app (PWA, v1.7):** la build genera `manifest.webmanifest` y `sw.js` al lado de `index.html` y de
  `dev/index.html` (la de dev se instala aparte, como «ChaskiBoom dev»). El service worker es *red primero*: siempre baja
  lo último y usa la caché solo sin conexión; no toca Firebase ni pedidos de audio por rangos. El artifact no lleva nada
  de esto (marcador `__PWA__` vacío).
- **Tablero 2D incremental (v1.12):** cada casilla tiene fijos su `<img class="pc">`, la marca `.mk` (dot/ring) y las
  coordenadas; `render2D()` solo cambia el `src` o `hidden` de lo que difiere. La pieza que vuela es la misma imagen de la casilla
  (se mueve el nodo). Las 12 piezas se precargan con `decode()`. Antes se recreaban las 64 casillas en cada jugada o selección
  y en iPhone el tablero parpadeaba.
  Desde v1.16 la imagen que vuela se queda en la casilla de destino (reemplaza la que había) en vez de cambiarle
  el `src` a la de destino: Safari tardaba un cuadro en redibujar el SVG y la pieza desaparecía un instante al aterrizar o comer.
- **Sonido en iPhone (v1.12):** Web Audio queda mudo con el interruptor de silencio. En iOS se reproduce en bucle
  un `<audio>` HTML con silencio (`iosAudioSession()`), que pasa la sesión a «reproducción». Se pausa al ocultar la página
  o al apagar el sonido. No se pudo probar en Safari real desde la nube (no hay WebKit).
- **Confeti y «Reducir movimiento» (v1.12):** con la opción de accesibilidad activada sale una versión suave
  (menos papelitos, sin giros, caen despacio desde arriba del cartel, 1,4 s). Daniel tiene la opción activada en su iPhone.
- **Diagnóstico de sonido:** agregar `?diag` a la dirección muestra el estado del audio (iOS, AudioContext, sonidos cargados,
  audio de silencio, cortes/intentos/recreado, reducir movimiento). En iPhone el juego suena solo mientras el `<audio>` de
  silencio está sonando: si iOS lo pausa, `keepPlay()` lo retoma y, si rechaza el play() en un toque, lo recrea.
- **Pantalla de carga (v1.14):** logo, barra y porcentaje. Los .glb se bajan todos a la vez (antes de a uno)
  y la barra avanza por bytes recibidos (`ASSET_SIZES`, marcador `__ASSET_SIZES__` que llena la build).
  `#loading` tiene z-index 60 para tapar la consola, que antes se veía encima.
- **Actualización automática (v1.15):** la build escribe `version.json` ({version, build}) al lado de cada página
  y mete el mismo código de build (`__BUILD__`, fecha y hora UTC) en la página. `checkUpdate()` lo consulta al abrir,
  al volver a la página o a la ventana, al reconectarse, al terminar una partida y cada 2 min (v1.23; antes 15 min).
  Si cambió y no se empezó ninguna partida, recarga sola; si hay una en curso o terminada, muestra un cartel
  (`#upd`) con Actualizar / Después. Para no recargar en bucle si la página llega vieja, se intenta una vez cada 10 min
  por versión (sessionStorage `chaskiboom.upd`). El service worker pide lo propio con `cache: 'no-cache'`
  (GitHub Pages deja cachear 10 min). En /dev/ también funciona: cada build nueva cuenta como versión nueva.
- **Logo en celular (v1.15):** `layout()` agranda `#logo` con el espacio que sobra sobre el tablero 2D
  (hasta el 80 % del ancho), sin achicar el tablero.
- **Botones bloqueados en partida (v1.17):** con una partida en curso (`inGame()` = empezada y sin terminar)
  Contra la CPU, Online y Nueva partida quedan deshabilitados (`lockGameButtons()` en `updateStatus`). Para empezar otra
  hay que terminarla o abandonarla. Para pasar a otra partida online sigue funcionando el aviso «Ver partida».
- **Service worker sin reemplazo a mitad de carga (v1.18):** antes el SW nuevo hacía `skipWaiting()` al instalarse.
  En iPhone eso mataba al viejo con las descargas de los .glb en curso y la carga quedaba trabada (pasó en el 45 %
  al actualizar a v1.17). Ahora el nuevo espera; `doUpdate()` lo activa con `postMessage('skipWaiting')` y recarga
  en `controllerchange` (tope 6 s). Vigía de carga: si no avanza en 20 s recarga sola una vez (sessionStorage
  `chaskiboom.stall`); si se repite, `loadFailed()` muestra «Reintentar».
- **Aviso de mensajes del chat (v1.18):** con el chat cerrado, un mensaje escrito del rival muestra 4 s abajo
  `#chatToast` («Pedro: …», tocarlo abre el chat) con un sonido suave; con la página oculta el título dice
  «💬 Pedro te escribió» (`chatAway` en `notifyTurn`). Las frases siguen con su cartel grande y el contador sigue igual.
- **Sonido de aviso (v1.19):** el «pin» de los avisos es el sonido de jaque (`check`). Ya no suena cuando el rival
  juega (`news(..., { quiet: true })`), porque la jugada tiene su propio sonido de movimiento: solo cambia el título
  y, al volver, se muestra el cartel sin sonido. En otras partidas la jugada del rival suena con la versión suave.
  Sigue sonando para desafío aceptado, partida comenzada, tablas, revancha y frases.
- **Premoves (v1.20):** contra la CPU u online, durante el turno del rival (incluso mientras se anima tu
  jugada) se toca una pieza propia y su destino; quedan en azul (`.sq2.pre` en 2D, `M.pre` en 3D). `tapSquare()`
  unifica los toques de 2D y 3D. Las jugadas posibles salen de `premovePos()` (la posición con tu color a mover).
  Con un premove anotado, cualquier toque lo cancela. `tryPremove()` se llama en `afterMove()` (online, cuando la
  cola de jugadas recibidas queda vacía): si es legal se juega, si no se avisa y se descarta. Se limpia al empezar
  o terminar la partida. No hay premoves entre dos jugadores en el mismo dispositivo.
- **Análisis de la partida (v1.21):** botón Analizar en el cartel de fin y en el Menú («Analizar partida» /
  «Ver análisis»). Stockfish a nivel 20 evalúa cada posición (`go depth 13 movetime 600`). Precisión por jugador con
  la fórmula de lichess; clasificación por probabilidad de ganar perdida (mejor/excelente <2/buena <5/imprecisión <10/
  error <20/metida de pata). Barra de evaluación (`#evalBar`, `body.analyzed`) al costado del tablero, que sigue a
  « ‹ › »; la clasificación aparece en el historial y en el renglón de abajo, con la mejor jugada. Precisión también
  en las barras de jugador. Nombres propios de la clasificación: Tremendo!! (★), Muy bueno!! (!), Bien ahí (✓),
  Y esto? (?!), Ah bue (?), Calambres (??). Al revisar, flecha verde fija con la mejor jugada (`showBest`, `#best2d`
  en 2D y `bestMat` en 3D; `arrowGeom/svgArrow/meshArrow` compartidas con la flecha de la última jugada). El resumen
  tiene un gráfico de la ventaja con puntos en Y esto?/Ah bue/Calambres; tocarlo lleva a esa jugada.
  El ícono de la clasificación también va sobre la pieza que hizo la jugada, arriba a la derecha (`#clsMark` dentro del
  tablero 2D; `#clsMark3d` proyectado desde la posición del personaje en cada cuadro en 3D, `placeClsMark3d`).
- **Revisión con sonido y meneo (v1.22):** al avanzar o retroceder de a una jugada (‹ ›, flechas del teclado)
  suena la jugada mostrada como en la partida (movimiento, comer, enroque, jaque) y la pieza hace el meneo; los saltos
  (« », gráfico) van en silencio (`stepReview`). En 2D cada pieza que aterriza hace un meneo corto (`wiggle()`,
  animación `land` de .38 s; con «Reducir movimiento», `landSoft`: rebote sin girar, desde v1.24).
- **Arrastrar y soltar (v1.25, solo 2D):** pointerdown en una pieza propia, a los 6 px se levanta (copia
  `.dragGhost` que sigue al puntero, destinos marcados, casilla bajo el dedo con `.hover`); al soltar en un destino
  legal se juega con `tapSquare(to)` y `dragDrop` hace que `move2d` no anime el vuelo. Sirve para premoves.
  Soltar en otro lado la devuelve y queda seleccionada. `#board2d { touch-action: none }`. En 3D no (arrastrar gira la cámara).
- **Elegir color contra la CPU (v1.26):** el cartel de Nueva partida tiene «Tu color» con tres botones con
  caballos del juego de piezas elegido: blancas, al azar (mitad y mitad) o negras. Se recuerda en localStorage
  `chaskiboom.color` (`colorPref` = w / r / b). Online y en dos jugadores sigue el sorteo. Desde v1.27 el cartel
  contra la CPU no lleva texto (`#mText` se oculta si está vacío); el color al azar se ve recién al comenzar.
- **Diseño:** tipografías Cinzel + EB Garamond; en PC columna lateral con logo y consola; en celular,
  consola plegable (historial + Menú).

## Historial reciente

- **v1.5:** el cartel de las frases para el rival dura 3 s (antes 1 s).
- **v1.6:** botón Cancelar en el cartel de Nueva partida contra la CPU.
- **v1.7:** instalable como app en el celular (PWA, íconos de `icono_chaskiboom.png`) y arranque en vista 2D.
- **v1.8:** avisos online sin servidor: novedades de la partida abierta al volver a la página y aviso con «Ver partida»
  para las otras partidas en curso.
- **v1.9:** sonido `come` al capturar (reemplaza al de movimiento), el swoosh del enroque suena al empezar el movimiento
  y la traslación en 2D es más rápida (0,35 s en vez de 0,5 s).
- **v1.10:** retratos `winner` / `loser` a la izquierda en los carteles de fin de partida.
- **v1.27:** el cartel de Nueva partida contra la CPU sin texto.
- **v1.26:** contra la CPU se elige el color (blancas, al azar o negras) con caballos.
- **v1.25:** arrastrar y soltar piezas en 2D (también para premoves).
- **v1.24:** meneo suave (rebote sin giro) al aterrizar cuando está activado «Reducir movimiento».
- **v1.23:** la búsqueda de versión nueva es cada 2 min y al volver a la ventana; no recarga sola con una partida terminada.
- **v1.22:** ícono de la clasificación sobre la pieza al revisar, sonidos de las jugadas en la revisión y meneo de
  la pieza al aterrizar en 2D.
- **v1.21:** análisis de la partida con Stockfish: precisión, clasificación con nombres propios, barra de evaluación,
  flecha verde con la mejor jugada y gráfico de la partida.
- **v1.20:** premoves contra la CPU y online (2D y 3D).
- **v1.19:** sin el «pin» de aviso cuando el rival juega (suena solo el movimiento).
- **v1.18:** el service worker nuevo ya no reemplaza al viejo a mitad de carga (en iPhone la carga quedaba trabada),
  vigía de carga con Reintentar, y aviso de los mensajes del chat con el chat cerrado.
- **v1.17:** Contra la CPU, Online y Nueva partida deshabilitados mientras hay una partida en curso.
- **v1.16:** 2D sin parpadeo al aterrizar o comer en iPhone (la imagen que vuela queda en la casilla de destino).
- **v1.15:** actualización automática de versión (`version.json`) y logo más grande en el celular.
  Quien tenía v1.14 o anterior tiene que cerrar y abrir la app una vez; desde ahí se actualiza sola.
- **v1.14:** pantalla de carga con logo, barra y porcentaje; los modelos se bajan en paralelo.
- **v1.13:** 20 juegos de piezas 2D nuevos de lichess (25 en total, licencias en `assets/pieces/LICENCIAS.md`)
  y el reloj de la CPU corre mientras piensa (`cpuThinking`; antes `busy` lo dejaba siempre en 0:00).
- **v1.12:** CPU Muy fácil y Fácil mucho más débiles (jugadas al azar), tablero 2D sin parpadeo en iPhone,
  sonido en iPhone con el modo silencio (audio de silencio en bucle que se recupera solo), confeti suave con «Reducir movimiento»
  y diagnóstico de sonido con `?diag`.
- **v1.11:** confeti de 1 s al ganar (`confetti()` en un canvas propio, sin librerías; respeta «reducir movimiento»).

## Pendientes / ideas

- **Probar los avisos de v1.8 con dos dispositivos reales:** desafío aceptado y jugada con la página minimizada
  o el celular bloqueado, y dos partidas en paralelo (aviso de la otra partida y «Ver partida»). Solo se probó con Firebase simulado.

- **Probar la instalación como app (v1.7):** Android (Chrome → Instalar app) e iPhone (Safari → Compartir → Agregar a inicio).
  Revisar ícono, pantalla completa, desafío por link y online. En iPhone la app instalada no comparte sesión con Safari:
  el usuario anónimo es otro, así que «Mis partidas» solo se conserva vinculando Google.
- **Probar Cancelar de v1.6 en producción:** con una partida en curso, tocar Nueva partida → Cancelar y verificar que quedan
  jugadas, relojes, lado del tablero y nivel de CPU como estaban. Solo se probó Cancelar desde la pantalla inicial.
- Mostrar el tablero 2D sin esperar a que bajen los modelos 3D (cargarlos por detrás).
- Partidas con tiempo límite (los relojes ya existen).
- Calibrar los niveles de la CPU con partidas reales.
- Logo nuevo con la "E" de BATTLE completa, exportado como PNG transparente.
- Depurar el online con jugadores reales.
