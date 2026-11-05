// Screenshot 1920x1080 de cada HTML do simulador (sim-NN.html -> sim-NN.png). Uso: node fotografar.js <arquivos.html...>
const puppeteer=require('puppeteer-core');const fs=require('fs'),path=require('path');
(async()=>{const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new'});
const p=await b.newPage();await p.setViewport({width:1920,height:1080});
const files=process.argv.slice(2);
for(const f of files){await p.goto('file://'+path.resolve(f),{waitUntil:'networkidle0'});await p.evaluate(()=>document.fonts.ready);
await p.screenshot({path:f.replace('.html','.png')});}
await b.close();console.log('ok')})();
