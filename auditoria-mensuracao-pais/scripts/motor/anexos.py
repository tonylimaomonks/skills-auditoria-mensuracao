# -*- coding: utf-8 -*-
"""Anexa ao relatório técnico TODOS os arquivos de evidência citados em C["EVIDENCIAS"].

Cada arquivo vira um bloco <script type="application/x-anexo"> com o conteúdo gzip+base64.
O HTML abre sozinho (sem a pasta evidencias/): o visualizador descompacta sob demanda
(DecompressionStream) e permite ver (imagem / JSON) e baixar o arquivo.

Credenciais: parâmetros de tag cuja chave indica token/segredo são mascarados em todos os
arquivos antes de embutir (o valor nunca entra no HTML). Imagens vão como JPEG (sips) para caber.
"""
import base64, glob, gzip, hashlib, json, os, re, subprocess, tempfile

MASK = "[MASCARADO: credencial em texto aberto na configuração; valor omitido do relatório]"
KEY_RE = re.compile(r"(access_?token|apiaccesstoken|api_?key|secret(?!proof)|password|senha|bearer)$", re.I)


def _collect_secrets(obj, out):
    if isinstance(obj, dict):
        k, v = obj.get("key"), obj.get("value")
        if isinstance(k, str) and isinstance(v, str) and KEY_RE.search(k) and len(v) >= 12 and "{{" not in v:
            out.add(v)
        for x in obj.values():
            _collect_secrets(x, out)
    elif isinstance(obj, list):
        for x in obj:
            _collect_secrets(x, out)


def resolve(root, ev):
    files = []
    for part in ev["arquivo"].split(" · "):
        part = part.split(" (")[0].strip()
        base = part if part.startswith("evidencias/") else os.path.join(os.path.dirname(files[-1]) if files else "", part)
        files += [os.path.relpath(p, root) for p in sorted(glob.glob(os.path.join(root, base)))]
    return files


def _img(path):
    tmp = tempfile.mktemp(suffix=".jpg")
    try:
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70", "-Z", "1800", path, "--out", tmp], check=True, capture_output=True)
        return open(tmp, "rb").read(), "image/jpeg", os.path.splitext(os.path.basename(path))[0] + ".jpg"
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


class Anexos:
    def __init__(self, root, evidencias):
        self.root = root
        self.by_ev = {ev["id"]: resolve(root, ev) for ev in evidencias}
        allf = sorted({f for fl in self.by_ev.values() for f in fl})
        secrets = set()
        for f in allf:
            if f.endswith(".json"):
                try:
                    _collect_secrets(json.load(open(os.path.join(root, f))), secrets)
                except Exception:
                    pass
        self.secrets = sorted(secrets, key=len, reverse=True)
        self.items = {}  # rel -> dict(id, name, mime, raw_sha, size, masked, b64)
        for i, f in enumerate(allf):
            p = os.path.join(root, f)
            raw = open(p, "rb").read()
            sha = hashlib.sha256(raw).hexdigest()
            masked = 0
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                data, mime, name = _img(p)
            else:
                txt = raw.decode("utf-8", "replace")
                for s in self.secrets:
                    if s in txt:
                        masked += txt.count(s)
                        txt = txt.replace(s, MASK)
                data, name = txt.encode(), os.path.basename(f)
                mime = "application/json" if f.endswith(".json") else "text/plain"
            self.items[f] = {"id": f"anx{i}", "name": name, "mime": mime, "sha": sha, "size": len(raw), "masked": masked,
                             "b64": base64.b64encode(gzip.compress(data, 9)).decode()}

    def link(self, rel, label=None):
        it = self.items.get(rel)
        if not it:
            return ""
        lab = label or os.path.basename(rel)
        return f'<button type="button" class="anx" data-anx="{it["id"]}">{lab}</button>'

    def blocks(self):
        out = []
        for rel, it in self.items.items():
            out.append(f'<script type="application/x-anexo" id="{it["id"]}" data-name="{it["name"]}" data-mime="{it["mime"]}" data-path="{rel}" data-masked="{it["masked"]}">{it["b64"]}</script>')
        return "".join(out)

    def total_mb(self):
        return sum(len(i["b64"]) for i in self.items.values()) / 1e6


CSS = """
button.anx{font:inherit;font-size:12px;border:1px solid var(--line);background:var(--accent-soft);color:var(--accent);border-radius:6px;padding:1px 7px;margin:1px 2px;cursor:pointer}
button.anx:hover{border-color:var(--accent)}
.evfiles{margin:0;padding:0;list-style:none}.evfiles li{margin:3px 0;line-height:1.35}.evfiles .sz{font-size:11px;color:var(--muted)}.evfiles .mk{font-size:11px;color:var(--crit-media)}
dialog.anxv{width:min(1200px,96vw);height:90vh;border:1px solid var(--line);border-radius:12px;padding:0;background:var(--paper);color:var(--ink)}
dialog.anxv::backdrop{background:rgba(0,0,0,.55)}
dialog.anxv .bar{display:flex;gap:8px;align-items:center;padding:10px 14px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--paper);flex-wrap:wrap}
dialog.anxv .bar b{flex:1;min-width:200px;word-break:break-all;font-size:14px}
dialog.anxv .bar input{font:inherit;font-size:13px;padding:3px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--ink)}
dialog.anxv .body{padding:12px 14px;height:calc(90vh - 60px);overflow:auto}
dialog.anxv .body img{max-width:100%;border:1px solid var(--line);border-radius:6px}
dialog.anxv .body pre{max-height:none;margin:0;font-size:12px}
dialog.anxv .note{font-size:12px;color:var(--muted);margin:0 0 8px}
@media print{dialog.anxv,button.anx{display:none}}
"""

JS = r"""
(function(){
 const dlg=document.createElement('dialog');dlg.className='anxv';dlg.setAttribute('aria-label','Anexo');
 dlg.innerHTML='<div class="bar"><b></b><input type="search" placeholder="Buscar no texto" aria-label="Buscar no texto"><button class="btn dl" type="button">Baixar</button><button class="btn cl" type="button">Fechar</button></div><div class="body"></div>';
 document.body.appendChild(dlg);
 const T=dlg.querySelector('b'),B=dlg.querySelector('.body'),Q=dlg.querySelector('input');let cur=null,txt='',url=null;
 dlg.querySelector('.cl').onclick=()=>dlg.close();
 dlg.addEventListener('close',()=>{if(!dlg.open)B.innerHTML=''});
 async function bytes(el){const bin=Uint8Array.from(atob(el.textContent.trim()),c=>c.charCodeAt(0));
  const s=new Blob([bin]).stream().pipeThrough(new DecompressionStream('gzip'));return new Uint8Array(await new Response(s).arrayBuffer())}
 function esc(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
 function render(){const v=Q.value.trim();const LIM=400000;let t=txt;
  if(v.length>1){const lines=txt.split('\n');const lv=v.toLowerCase();const hit=lines.map((l,i)=>[i+1,l]).filter(x=>x[1].toLowerCase().includes(lv));
   t=hit.length?hit.slice(0,5000).map(x=>String(x[0]).padStart(7)+'  '+x[1]).join('\n'):'(nenhuma linha contém “'+v+'”)'}
  const cut=t.length>LIM;B.innerHTML='<pre><code>'+esc(cut?t.slice(0,LIM):t)+'</code></pre>'+(cut?'<p class="note">Exibição limitada aos primeiros 400 mil caracteres; use a busca ou “Baixar” para o arquivo completo.</p>':'')}
 Q.addEventListener('input',()=>{clearTimeout(render.t);render.t=setTimeout(render,250)});
 dlg.querySelector('.dl').onclick=()=>{if(!cur)return;const a=document.createElement('a');a.href=url;a.download=cur.dataset.name;document.body.appendChild(a);a.click();a.remove()};
 document.addEventListener('click',async ev=>{const b=ev.target.closest('button.anx');if(!b)return;const el=document.getElementById(b.dataset.anx);if(!el)return;
  if(url){URL.revokeObjectURL(url);url=null}const tk=(render.tk=(render.tk||0)+1);cur=el;T.textContent=el.dataset.path;B.innerHTML='<p class="note">Carregando…</p>';Q.value='';dlg.showModal();
  try{const by=await bytes(el);if(tk!==render.tk)return;const mime=el.dataset.mime;url=URL.createObjectURL(new Blob([by],{type:mime}));
   const mk=+el.dataset.masked;const note=mk?'<p class="note">'+mk+' credencial(is) mascarada(s) neste arquivo.</p>':'';
   if(mime.startsWith('image/')){Q.hidden=true;B.innerHTML=note+'<img alt="'+esc(el.dataset.path)+'" src="'+url+'">'}
   else{Q.hidden=false;txt=new TextDecoder().decode(by);if(mime==='application/json'&&txt.length<3e6){try{txt=JSON.stringify(JSON.parse(txt),null,2)}catch(e){}}
    render();if(note)B.insertAdjacentHTML('afterbegin',note)}}
  catch(e){B.innerHTML='<p class="note">Não foi possível abrir o anexo neste navegador ('+esc(String(e))+'). Use Chrome, Edge, Safari 16.4+ ou Firefox 113+.</p>'}});
})();
"""
