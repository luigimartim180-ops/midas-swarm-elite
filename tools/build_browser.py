"""Gera um navegador de arquivos estático (browse.html) a partir do repositório.

Uso: python3 tools/build_browser.py [saida.html]
Lê os arquivos versionados (git ls-files) e embute o conteúdo num JSON, para
funcionar sem servidor de aplicação — basta servir a pasta por HTTP.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 400_000


def tracked_files():
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    return [f for f in out if f]


def build(saida: Path):
    arquivos = []
    for rel in tracked_files():
        p = ROOT / rel
        if not p.is_file():
            continue
        raw = p.read_bytes()
        truncado = len(raw) > MAX_BYTES
        texto = raw[:MAX_BYTES].decode("utf-8", errors="replace")
        arquivos.append({
            "path": rel,
            "bytes": len(raw),
            "linhas": texto.count("\n") + 1,
            "truncado": truncado,
            "conteudo": texto,
        })
    arquivos.sort(key=lambda a: a["path"])
    dados = json.dumps(arquivos, ensure_ascii=False)
    saida.write_text(TEMPLATE.replace("__DADOS__", dados), encoding="utf-8")
    print(f"{saida} — {len(arquivos)} arquivos, {saida.stat().st_size} bytes")


TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Arquivos do projeto — SWARM v3</title>
<style>
  :root{--bg:#0f1115;--panel:#171a21;--line:#272b34;--fg:#e6e8ee;--muted:#8b93a7;--accent:#4c8dff;--code:#0b0d11}
  *{box-sizing:border-box}
  body{margin:0;font:14px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--bg);color:var(--fg)}
  header{position:sticky;top:0;z-index:5;background:var(--panel);border-bottom:1px solid var(--line);padding:12px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
  header h1{font-size:15px;margin:0;font-weight:600}
  header .tag{color:var(--muted);font-size:12px}
  input[type=search]{flex:1;min-width:200px;background:var(--code);border:1px solid var(--line);color:var(--fg);border-radius:8px;padding:8px 10px;font:inherit}
  .wrap{display:grid;grid-template-columns:280px 1fr;min-height:calc(100vh - 57px)}
  nav{border-right:1px solid var(--line);background:var(--panel);overflow:auto;max-height:calc(100vh - 57px);position:sticky;top:57px}
  nav button{display:block;width:100%;text-align:left;background:none;border:0;color:var(--fg);padding:8px 14px;font:inherit;cursor:pointer;border-bottom:1px solid #1d212a}
  nav button:hover{background:#1f2430}
  nav button.on{background:var(--accent);color:#fff}
  nav button small{color:var(--muted);display:block;font-size:11px}
  nav button.on small{color:#dbe7ff}
  main{padding:0;overflow:auto;max-height:calc(100vh - 57px)}
  .head{padding:10px 16px;border-bottom:1px solid var(--line);color:var(--muted);font-size:12px;position:sticky;top:0;background:var(--bg)}
  pre{margin:0;padding:16px;overflow:auto;background:var(--code);white-space:pre;tab-size:2}
  .aviso{padding:10px 16px;color:#ffcf70;background:#2a2413;border-bottom:1px solid var(--line)}
</style>
</head>
<body>
<header>
  <h1>&#128193; Arquivos do projeto</h1>
  <span class="tag" id="tag"></span>
  <input type="search" id="busca" placeholder="Filtrar por nome do arquivo... (ex: engine, README)">
</header>
<div class="wrap">
  <nav id="lista"></nav>
  <main>
    <div class="head" id="cabecalho">Escolha um arquivo</div>
    <div id="conteudo"></div>
  </main>
</div>
<script id="dados" type="application/json">__DADOS__</script>
<script>
"use strict";
const arquivos = JSON.parse(document.getElementById("dados").textContent);
const lista = document.getElementById("lista");
const cabecalho = document.getElementById("cabecalho");
const conteudo = document.getElementById("conteudo");
const busca = document.getElementById("busca");

document.getElementById("tag").textContent =
  arquivos.length + " arquivos versionados · " +
  (arquivos.reduce((s,a)=>s+a.bytes,0)/1024).toFixed(1) + " KB";

function mostrar(a){
  cabecalho.textContent = a.path + "  —  " + a.bytes + " bytes, " + a.linhas + " linhas";
  conteudo.innerHTML = "";
  if (a.truncado){
    const d = document.createElement("div");
    d.className = "aviso";
    d.textContent = "Arquivo grande: mostrando os primeiros 400 KB.";
    conteudo.appendChild(d);
  }
  const pre = document.createElement("pre");
  pre.textContent = a.conteudo;
  conteudo.appendChild(pre);
}

function render(filtro){
  const f = (filtro||"").toLowerCase();
  lista.innerHTML = "";
  arquivos.filter(a => a.path.toLowerCase().includes(f)).forEach(a => {
    const b = document.createElement("button");
    const nome = a.path.split("/").pop();
    const dir = a.path.includes("/") ? a.path.slice(0, a.path.lastIndexOf("/")) + "/" : "";
    b.appendChild(document.createTextNode(nome));
    const s = document.createElement("small");
    s.textContent = dir + " · " + a.bytes + " B";
    b.appendChild(s);
    b.addEventListener("click", () => {
      [...lista.children].forEach(c => c.classList.remove("on"));
      b.classList.add("on");
      mostrar(a);
    });
    lista.appendChild(b);
  });
}

busca.addEventListener("input", () => render(busca.value));
render("");
if (arquivos.length) { lista.children[0].click(); }
</script>
</body>
</html>
"""


if __name__ == "__main__":
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "browse.html"
    build(destino)
