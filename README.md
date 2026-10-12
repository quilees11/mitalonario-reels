# mitalonario-reels

Vídeos de Talonario (mitalonario.es) para TikTok, Instagram y Facebook.

- `guiones/AAAA-MM-DD.json`: guion, música y caption de cada reel.
- `render.py`: genera el MP4 (1080x1920) a partir del guion. Fuentes Inter (OFL) en `fonts/`.
- `.github/workflows/reels.yml`: GitHub Actions genera los vídeos que falten en `reels/` al subir un guion nuevo y los lunes, miércoles y viernes.
- Los vídeos se publican en `https://quilees11.github.io/mitalonario-reels/reels/reel_AAAA-MM-DD.mp4` y una tarea de Claude los programa en Metricool.
