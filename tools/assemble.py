#!/usr/bin/env python3
"""src/main.js(번들) + src/index.html + config.json + data/scene.json -> dist/index.html"""
import json, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parent.parent
subprocess.run(['npx', 'esbuild', 'src/main.js', '--bundle', *([] if __import__('os').environ.get('NOMIN') else ['--minify']), '--format=iife', '--target=es2020',
                '--legal-comments=none', '--outfile=dist/bundle.js'], cwd=root, check=True)
html = (root / 'src/index.html').read_text()
cfg = json.loads((root / 'config.json').read_text())
cfg.setdefault('antipode', '우루과이 앞바다(남대서양)')
safe = lambda s: s.replace('</', '<\\/')
html = html.replace('/*CONFIG*/', safe(json.dumps(cfg, ensure_ascii=False)))
html = html.replace('/*SCENE*/', safe((root / 'data/scene.json').read_text()))
html = html.replace('/*BUNDLE*/', safe((root / 'dist/bundle.js').read_text()))
out = root / 'dist/index.html'
out.write_text(html)
print(out, out.stat().st_size // 1024, 'KB')
