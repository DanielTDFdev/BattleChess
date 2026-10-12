# ChaskiBoom Battle Chess

Ajedrez web en 3D donde las piezas pelean cuando se capturan, con vista 2D clásica.

© 2026 Daniel Camargo

## Cómo correrlo

Es un sitio estático: no necesita compilación. Para probarlo en tu PC, serví la carpeta con cualquier servidor local
(abrir `index.html` con doble clic no funciona, porque el navegador bloquea la carga de los modelos desde el disco):

```
python -m http.server 8000
```

y abrí http://localhost:8000

## Créditos

- Personajes, armas y animaciones: [KayKit](https://kaylousberg.com) de Kay Lousberg (CC0).
- Piezas 2D (tomadas de [lichess](https://github.com/lichess-org/lila)):
  - Cburnett: Colin M.L. Burnett, GPLv2+.
  - Merida: Armando Hernández Marroquín, GPLv2+.
  - Chessnut: Alexis Luengas, Apache 2.0.
  - Celtic y Fantasy: Maurizio Monge, MIT.
- CPU: [Stockfish](https://stockfishchess.org) vía [Stockfish.js](https://github.com/nmrugg/stockfish.js) 18 (versión lite), GPLv3. La licencia está en `assets/engine/Copying.txt` y el código fuente en esos enlaces.
- Motor 3D: [three.js](https://threejs.org) r147. Reglas de ajedrez: [chess.js](https://github.com/jhlywa/chess.js) 0.10.3.
- Tipografías: Cinzel y EB Garamond (Google Fonts, SIL Open Font License).
