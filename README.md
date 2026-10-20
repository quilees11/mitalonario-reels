# mitalonario-reels

Vídeos de Talonario (mitalonario.es) para TikTok, Instagram y Facebook.

- `guiones/AAAA-MM-DD.json`: guion, música y caption de cada reel.
- `render.py`: genera el MP4 (1080x1920) a partir del guion. Fuentes Inter (OFL) en `fonts/`.
- `.github/workflows/reels.yml`: GitHub Actions genera los vídeos que falten en `reels/` al subir un guion nuevo y cada día a las 04:15 UTC.
- Los vídeos se publican en `https://quilees11.github.io/mitalonario-reels/reels/reel_AAAA-MM-DD.mp4` y una tarea de Claude los programa en Metricool.

- Un reel diario: martes, sábado y domingo, la suite Talonario completa; lunes, miércoles, jueves y viernes, un módulo rotando: Residuos (DeI) · Cartas de Porte (DeCA) · Gestor de Contraseñas · Sistema de Fichajes · Soporte Informático (ver `generar_guion.py`). Cada reel dura 25,2 s y acaba con precio (Soporte: presupuesto a medida) y contacto. No se promocionan la licencia de facturación ni las Copias de seguridad.
