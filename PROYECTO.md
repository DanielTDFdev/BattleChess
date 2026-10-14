# ChaskiBoom Battle Chess — notas del proyecto

Documento de trabajo para retomar el desarrollo (también sirve de contexto para Claude).

## Qué es

Ajedrez web de Daniel Camargo, inspirado en el Battle Chess de su infancia: cuando una pieza captura a otra,
pelean una batalla corta en 3D. Tiene vista 2D clásica, CPU con niveles y modo online entre amigos.

- Sitio: https://danieltdfdev.github.io/BattleChess/ (GitHub Pages, rama `main`, raíz)
- Copia de pruebas: https://danieltdfdev.github.io/BattleChess/dev/
- Repo: https://github.com/DanielTDFdev/BattleChess (se movió desde `danieltdfdev/battlechess`; usar esta URL como remoto)
- Versión actual: **v1.39** (ver `<span id="ver">` en `src/game_template.html`)

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
3. Cuando Daniel dice **"publicar"** (o "subilo a producción"): subir la versión en el template (v1.39 → v1.40…; v2.0 para saltos grandes),
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
  Desde v1.31 solo se bloquean con una partida local (CPU o dos jugadores): de una online se puede salir sin
  abandonarla (queda en «Mis partidas»); «Contra la CPU» la deja con `leaveOnline()` y abre el cartel de nueva partida.
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
- **CPU sin Stockfish (v1.28):** en redes con firewall (p. ej. Fortinet en la oficina de Daniel) el `.wasm` de Stockfish
  no llega. `sfInit()` hace un `HEAD` aparte al `.wasm`: si falla o no viene con tipo wasm, pasa al motor propio enseguida
  (antes Stockfish quedaba colgado hasta el tope de 25 s). Sin conexión no se apura, porque puede estar en la caché.
  El motor propio (`bestAt` + `negamax`, profundidad `fb` del nivel) corre en un Web Worker armado como blob con
  `Chess.toString()` y esas funciones (`fbWorkerGet`/`fallbackMove`); si no se puede crear, calcula en la página como antes.
  A profundidad 3 tarda unos 4 s y congelaba la pantalla. Con el motor simple, la barra del rival dice «CPU difícil (simple)».
- **Reloj exacto (v1.28):** `clockFlush()` asigna el tiempo transcurrido según el estado; se llama en el tic de 200 ms y en
  cada cambio de estado (empieza/termina de pensar la CPU, empieza/termina una jugada). Antes, si la pantalla se trababa
  mientras pensaba la CPU, no caía ningún tic adentro y ese tiempo se perdía.
- **Correspondencia (v1.30):** al desafiar se elige «Tiempo por jugada»: 1, 3 o 7 días o sin límite (localStorage
  `chaskiboom.perMove`, por defecto sin límite). En la partida: `perMove` (ms; 0 = sin límite; las viejas no lo tienen) y
  `deadline` (hora del servidor, `srvNow()` con `.info/serverTimeOffset`), que escriben las blancas al tocar Comenzar y cada
  jugada en el mismo `update`. Al vencer se pierde; si al que le sobra tiempo solo le queda el rey, tablas (`timeout` /
  `timeoutDraw`). No hay servidor: cualquier cliente que vea la partida vencida la cierra (`claimTimeout`, cada 20 s, al abrirla,
  en el vigía y en «Mis partidas»); las reglas aceptan ese resultado solo si `deadline < now`, `deadline` solo cambia junto
  con `ply` y no puede pasar de `now + perMove`. Relojes: al que le toca, lo que le queda (rojo con menos de 12 h); al otro, el
  plazo («3d»). Quien acepta ve el plazo antes de entrar aunque ya tenga apodo. La revancha hereda el plazo. Avisos solo en la
  app: resumen al abrir o al volver tras 1 min afuera («Te toca en 2 partidas · una vence en 4 h», `turnSummary`, en rojo con
  menos de 12 h) y, después de cada jugada con plazo, «Avisar por WhatsApp» (`wa.me` con el link). «Mis partidas» pone primero
  las que te tocan, por vencimiento, con la etiqueta del plazo. Prueba con mock: `test_corr.py` (no está en el repo).
- **Desafíos que vencen y borrar partidas (v1.32):** un desafío sin aceptar vence a las 24 h de `createdAt`
  (`inviteExpired`). No hay servidor: lo borra de la base (y del índice) la app de quien lo creó al verlo vencido, en
  «Mis partidas» o en el vigía; quien abre un link vencido ve «Desafío vencido» y las reglas no lo dejan entrar
  (`guest` exige `createdAt > now - 24 h`). En «Mis partidas», ✕ (dos toques: ✕ → «Quitar ahora» en rojo durante 5 s; antes decía «Cancelar» y se entendía como no borrar) en los desafíos pendientes
  (borra `games/<código>`; regla `.write` en `$g` solo para borrar entero, del creador y sin `guest`) y en las terminadas
  (solo quita `users/<uid>/games/<código>`; al rival le queda). Las en curso no tienen ✕. También se limpian del índice
  las partidas que ya no existen.
- **Mensaje del desafío (v1.33):** Compartir y Copiar mandan el mensaje entero con el link al final: «Daniel te desafía a
  una partida de ChaskiBoom Battle Chess a 3 días por jugada. Aceptá entrando a este link (el desafío vence en 24 h): …».
  Va todo en `text` de `navigator.share` (sin `url` aparte), porque WhatsApp a veces descarta el texto si el link va separado.
- **Planilla de jugadas (v1.34):** solo en PC (`body.wide`), `<ol id="moves">` en la columna izquierda entre el estado
  y la consola (`layout()` le da `top` y `maxHeight`; se oculta si quedan menos de 90 px). Dos columnas con el ícono de la
  pieza (`pieceImg`, el juego de piezas elegido; las negras con borde claro) y la jugada sin la letra de la pieza; enroques
  como O-O. Con el análisis hecho muestra la clasificación. Tocar una jugada = `viewAt(n)` (la última, `goLive()`); la que
  se ve queda marcada y a la vista. `renderMoves(n)` se llama desde `updateHist()` y rehace la lista solo si cambian las
  jugadas, el juego de piezas o el análisis.
- **Aviso fijo de partidas pendientes (v1.35):** en la pantalla inicial («¿Cómo querés jugar?») un recuadro fijo
  `#pend` («Te toca en la partida contra X · vence en …» o «Te toca en N partidas online»; rojo con menos de 12 h) que abre
  «Mis partidas». En el botón Online de la consola, un número (`#monBadge`) con las partidas en las que te toca.
  `pendingGames()` / `updatePending()` usan las partidas del vigía (no la abierta); se actualizan con cada novedad y cada
  minuto. Con la pantalla inicial a la vista, `turnSummary` no muestra el aviso de arriba (sería repetido).
- **Vigía sin depender del apodo y reconexión al volver (v1.37):** el aviso de «te toca» no aparecía hasta entrar a
  Online. Dos causas posibles, se arreglaron las dos: (1) el vigía arrancaba solo si había apodo en localStorage; ahora
  `fbResume()` arranca si hay una sesión de Firebase guardada (sin sesión no se conecta, para no crear anónimos).
  (2) en el celular, con la app en segundo plano la conexión muere y Firebase no se entera: al volver tras más de 10 s se
  hace `db.goOffline(); db.goOnline()` y llegan las novedades. Con `.info/connected` se vuelve a marcar la presencia en la
  partida abierta (antes, tras una reconexión el rival te veía desconectado). Probado con el mock; falta probar en el celular.
- **Premove solo contra la CPU; confirmación en correspondencia (v1.35):** los premoves funcionan solo contra la
  CPU (`canPremove`); en todas las online no (más adelante, en las online con reloj corto: 3 min, 10 min, 3+2…). En las
  partidas con plazo (`isCorr()`, `perMove > 0`) cada jugada se confirma: `askConfirm` la muestra en el tablero 2D
  (`render2D({ pos })`; en 3D queda marcada) y abre `#confirm` («¿Confirmás movimiento?» · Sí / Cancelar). Va centrado sobre el
  tablero, a la altura que no tapa el origen ni el destino (`placeConfirm`, prueba franjas desde el medio; en 3D proyecta
  las casillas con la cámara). Sí la envía (en 2D aterriza sin vuelo, `dragDrop`); Cancelar o Esc la vuelve atrás sin
  dejar nada seleccionado. Se cancela sola al terminar la partida, salir de ella o revisar el historial.
- **Blitz y Rápida online (v1.38):** al desafiar se elige el modo: Blitz 3 min, 3+2, 5 min; Rápida 10 min, 10+5, 15+10;
  correspondencia 1/3/7 días o sin límite (localStorage `chaskiboom.mode`: `3+2`, `d3`…; migra el viejo `chaskiboom.perMove`).
  Bala quedó afuera hasta medir cuánto pesa la conexión. En la partida: `tc = { base, inc }` (ms) y `clock = { w, b }`, lo que
  le quedaba a cada uno en `lastMoveAt` (hora del servidor). Al que le toca se le descuenta lo que pasó desde ahí
  (`clockLeft`), así los dos ven el mismo reloj. Quien juega escribe en el mismo update su reloj menos lo usado más el
  incremento. Los relojes arrancan después de la primera jugada de cada uno; si alguno no la hace en 30 s, la partida se
  anula (`aborted`). La bandera se reclama con `timeoutResult`/`claimTimeout` (en el tic de 200 ms, medio segundo de margen).
  Con la bandera caída no se puede jugar. Si el rival se desconecta (presencia `online/<uid>`) más de 30 s, cartel «Tu
  rival se fue» con Reclamar la victoria (`left`) / Esperar (`checkGone`); si vuelve, se cierra. En Blitz no hay peleas 3D
  (captura rápida); en Rápida sí, y la pelea corre en el reloj del que la mira. Premoves habilitados en las partidas con reloj.
  El mensaje del desafío dice el modo («…a una partida Blitz (3+2) de ChaskiBoom Battle Chess…», `modeName`); «Mis partidas»
  muestra la etiqueta (`modeTag`, «3+2»). La revancha hereda el modo (`gameMode`). Reglas nuevas: `tc`, `clock` (no puede
  subir más que el incremento), `lastMoveAt` (= `now`), y `result` acepta `timeout` con reloj, `aborted` y `left` solo si
  corresponde. No se pudieron probar las reglas en el emulador (no se puede bajar en la nube). Prueba con mock: `test_tc.py`.
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
- **v1.39:** en el cartel de Online, «Entrar con Google» con el logo de Google (SVG inline, `G_LOGO`) y el texto
  «Sin cuenta: tus partidas quedarán solo en este dispositivo.»
- **v1.38:** partidas online Blitz (3, 3+2, 5) y Rápida (10, 10+5, 15+10) con reloj del servidor, anulación si no se
  juega la primera en 30 s, reclamo de victoria si el rival se va 30 s, premoves con reloj, Blitz sin peleas y el modo
  en el mensaje del desafío. Reglas nuevas.
- **v1.37:** el aviso de «te toca» aparece en la pantalla inicial sin entrar a Online (vigía con sesión guardada aunque
  no haya apodo, reconexión forzada al volver a la app) y la presencia se vuelve a marcar tras una reconexión.
- **v1.36:** la confirmación de jugada sale centrada sobre el tablero, sin tapar el origen ni el destino.
- **v1.35:** aviso fijo de partidas pendientes en la pantalla inicial y número en el botón Online; en las partidas con
  plazo, «¿Confirmás movimiento?» (Sí / Cancelar) antes de enviar cada jugada; premoves solo contra la CPU.
- **v1.34:** planilla de jugadas con íconos de las piezas en la columna izquierda (solo PC); tocar una jugada lleva a esa posición.
- **v1.33:** Compartir y Copiar mandan el mensaje del desafío con el plazo y el link; la confirmación del ✕ dice «Quitar ahora».
- **v1.32:** los desafíos sin aceptar vencen a las 24 h y se borran; ✕ en «Mis partidas» para cancelar desafíos o quitar
  partidas terminadas de la lista. Reglas nuevas (borrado del desafío y `guest` con `createdAt`).
- **v1.31:** se puede salir de una partida online sin abandonarla (Contra la CPU, Online y Nueva partida habilitados).
- **v1.30:** partidas por correspondencia: plazo por jugada (1, 3, 7 días o sin límite), se pierde al vencer
  (tablas si al otro solo le queda el rey), relojes con lo que queda, resumen «Te toca en…» al abrir, «Mis partidas» por
  vencimiento y «Avisar por WhatsApp» después de jugar. Reglas nuevas de `perMove`, `deadline` y `result`.
- **v1.29:** en el resumen del análisis, más espacio entre el ícono de la clasificación y su nombre
  (`#modal .anaSum td .cls`, 9 px a la derecha y sin margen a la izquierda).
- **v1.28:** CPU sin Stockfish (firewall) sin congelar la pantalla, detección rápida del `.wasm` bloqueado, aviso
  «(simple)» en el nombre de la CPU y reloj de la CPU exacto.
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

- **Pegar `database.rules.json` en la consola de Firebase antes de probar Blitz/Rápida** (reglas de `tc`, `clock`,
  `lastMoveAt` y los nuevos resultados). Probar con dos dispositivos: bandera, anulación a los 30 s, rival que se va.
- Bala (1, 1+1, 2+1) y «Más controles de tiempo», después de medir el retraso de la conexión.

- **Pegar `database.rules.json` en la consola de Firebase antes de probar v1.30** (reglas de `perMove`, `deadline` y `result`).
  Sin eso el vencimiento igual se registra, pero sin validar que el plazo haya pasado. Probar con dos dispositivos a 1 día.

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
