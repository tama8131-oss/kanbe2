const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:560,height:800}});
  await p.goto('file://' + process.argv[2]); await p.emulateMedia({media:'print'});
  await p.waitForTimeout(500);
  const r = await p.evaluate(() => [...document.querySelectorAll('section.pg')].map((s,i)=>{
     const inn=s.querySelector('.in'); const L=s.closest('.L'); 
     let over = inn.scrollHeight - inn.clientHeight;
     // also find descendants extending beyond .in bottom
     const ib = inn.getBoundingClientRect().bottom; let m=0;
     inn.querySelectorAll('*').forEach(e=>{const rb=e.getBoundingClientRect().bottom; if(rb-ib>m) m=rb-ib;});
     return [s.id, L?L.className:'', Math.round(Math.max(over,m)), ((s.querySelector('h1')||{}).textContent||'').slice(0,40)];
  }).filter(x=>x[2]>2));
  console.log(JSON.stringify(r)); await b.close(); })();
