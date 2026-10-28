const { chromium } = require('playwright');
const U=__dirname+'/frames/';
const OUT=__dirname+'/';
const Y='#F9EB1E';
const LOGO='data:image/png;base64,'+require('fs').readFileSync(__dirname+'/logo-muros.png').toString('base64');
const logo=(bg)=>`<div class="logo"${bg?' style="background:#111;padding:18px 22px;border-radius:10px"':''}><img src="${LOGO}"></div>`;
const css=`*{margin:0;box-sizing:border-box}body{width:1080px;height:1350px;font-family:Inter;overflow:hidden;position:relative;background:#111}
.ph{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.sh{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,0) 45%,rgba(0,0,0,.88) 100%)}
.logo{position:absolute;top:56px;left:64px;display:flex;flex-direction:column;line-height:1}
.logo{top:48px}.logo img{width:230px;display:block;filter:drop-shadow(0 2px 8px rgba(0,0,0,.45))}
.num{position:absolute;top:62px;right:64px;color:#fff;font-weight:600;font-size:24px;letter-spacing:3px;opacity:.9}
.txt{position:absolute;left:64px;right:64px;bottom:96px;color:#fff}
.tag{display:inline-block;background:${Y};color:#111;font-weight:800;font-size:26px;letter-spacing:4px;padding:10px 18px;margin-bottom:28px;text-transform:uppercase}
h1{font-weight:800;font-size:92px;line-height:.98;letter-spacing:-2px}
h1 em{font-style:normal;color:${Y}}
p{font-size:36px;line-height:1.3;margin-top:26px;font-weight:500;opacity:.95}
.swipe{position:absolute;bottom:40px;right:64px;color:#fff;font-size:22px;letter-spacing:3px;font-weight:600;opacity:.8}`;
const slide=(img,pos,tag,h,p,i)=>`<html><head><style>${css}</style></head><body>
<img class="ph" src="data:image/jpeg;base64,${require('fs').readFileSync(U+img).toString('base64')}" style="object-position:${pos}"><div class="sh"></div>${logo()}
<div class="num">0${i}/07</div><div class="txt"><div class="tag">${tag}</div><h1>${h}</h1><p>${p}</p></div>
${i<7?'<div class="swipe">DESLIZÁ →</div>':''}</body></html>`;
const slides=[
 slide('stageB.jpg','50% 0%','Zumba · Profe Gaby','Subí el volumen.<br>Entrená <em>bailando.</em>','Música, ritmo y energía que te cambian el día.',1),
 slide('crowd.jpg','50% 55%','Energía en grupo','Un salón lleno<br>de <em>buena onda.</em>','Te contagiás del ritmo de todas y no querés parar.',2),
 slide('pink.jpg','50% 40%','Cardio','Quemás calorías<br><em>sin darte cuenta.</em>','Trabajás resistencia, coordinación y todo el cuerpo mientras te divertís.',3),
 slide('smile.jpg','50% 30%','Disfrutá','Acá se viene<br>a <em>sonreír.</em>','Soltás el estrés, te reís y salís renovada.',4),
 slide('late.jpg','50% 35%','Para todas','Sin experiencia.<br><em>Sin edades.</em>','No hace falta saber bailar: seguís los pasos a tu ritmo.',5),
 slide('stageA.jpg','50% 35%','Entrenamiento consciente','Gaby te guía<br><em>paso a paso.</em>','Movimiento con alegría y cuidando tu cuerpo. Eso es Muros.',6),
 `<html><head><style>${css}
 body{background:${Y}}.c{position:absolute;inset:0;padding:64px;display:flex;flex-direction:column;justify-content:center;color:#111}
 .c h1{font-size:110px}.c .k{font-size:30px;letter-spacing:5px;font-weight:700;margin-bottom:24px}
 .box{margin-top:60px;background:#111;color:#fff;padding:44px 48px;border-radius:6px}
 .row{font-size:40px;font-weight:700;display:flex;gap:22px;align-items:center}.row+.row{margin-top:26px}
 .row b{color:${Y};font-size:24px;letter-spacing:3px;width:190px;font-weight:800}
 .cta{margin-top:56px;font-size:38px;font-weight:800}</style></head><body>${logo(true)}<div class="num" style="color:#111">07/07</div>
 <div class="c"><div class="k">ZUMBA CON LA PROFE GABY</div><h1>Vení a<br>bailar con<br>nosotras.</h1>
 <div class="box"><div class="row"><b>DIRECCIÓN</b>Av. Mitre 926, Campana</div><div class="row"><b>WHATSAPP</b>3489 588703</div></div>
 <div class="cta">Escribinos y reservá tu lugar →</div></div></body></html>`];
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1350}});
for(let i=0;i<slides.length;i++){await pg.setContent(slides[i],{waitUntil:'load'});await pg.screenshot({path:`${OUT}slide-0${i+1}.png`});}
await b.close();})();
