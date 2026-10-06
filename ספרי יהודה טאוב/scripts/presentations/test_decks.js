const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
const dir='/home/user/aaa/ספרי יהודה טאוב/פרשת שבוע וחגים/שיעורי קול תודה -  פרשת השבוע/001 בראשית/';
const only=process.argv[2];
(async()=>{
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
 const files=fs.readdirSync(dir).filter(f=>f.startsWith('מצגת - ')&&f.endsWith('.html')&&(!only||f.includes(only)));
 for(const fn of files){
  for(const [name,vp] of [['d',{width:1280,height:800}],['m',{width:390,height:780}]]){
   const p=await b.newPage({viewport:vp}); const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
   await p.goto('file://'+dir+encodeURI(fn)); await p.waitForTimeout(400);
   const total=await p.evaluate(()=>document.querySelectorAll('.slide').length); const issues=[];
   for(let i=0;i<total;i++){
     await p.waitForTimeout(650);
     const r=await p.evaluate(()=>{const s=document.querySelector('.slide.active');const sc=s.querySelector('.scroll');return {hx:document.documentElement.scrollWidth>innerWidth+2||s.scrollWidth>s.clientWidth+2||sc.scrollWidth>sc.clientWidth+2,tall:sc.scrollHeight>sc.clientHeight+2}});
     if(r.hx) issues.push('H'+(i+1)); if(r.tall && name==='d') issues.push('tall'+(i+1));
     if(process.argv[3]==='shot') await p.screenshot({path:`/tmp/pres/shots/${name}_${i+1}.png`});
     if(i<total-1) await p.keyboard.press('ArrowLeft');
   }
   // quizzes
   const nq=await p.evaluate(()=>document.querySelectorAll('.qbox').length); let qok=0;
   for(let q=0;q<nq;q++){
     const res=await p.evaluate((q)=>{const bx=document.querySelectorAll('.qbox')[q];const c=+bx.dataset.correct;const opts=bx.querySelectorAll('.opt');const w=(c+1)%opts.length;
       opts[w].click();const bad=bx.querySelector('.feedback').classList.contains('bad');bx.querySelector('.retry').click();opts[c].click();return bad&&opts[c].classList.contains('correct')&&opts.length===4},q);
     if(res)qok++; }
   console.log(fn.slice(7,40),name,'slides',total,'quiz',qok+'/'+nq,'issues',issues.join(','),'errs',errs.slice(0,2).join('|'));
   await p.close();
  }
 }
 await b.close();})();
