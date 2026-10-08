const { chromium } = require('playwright');
(async()=>{
 const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
 const p = await b.newPage();
 for (const f of require('fs').readFileSync('/tmp/bk.txt','utf8').split('\n').filter(Boolean)){ await p.goto('file://'+f); await p.waitForTimeout(400);
   await p.pdf({path:f.replace(/\.html$/,'.pdf'),format:'A4',printBackground:true,margin:{top:'14mm',bottom:'14mm',left:'12mm',right:'12mm'}}); console.log('pdf',f.split('/').pop()); }
 await b.close();})();
