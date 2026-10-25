const { chromium } = require('playwright');
const U='/root/.claude/uploads/7877332c-b3d8-56d2-bff0-a9a67fff7e2d/';
const OUT='/home/user/PEPI/carrusel-pilates-muros/';
const Y='#F7E018';
const logo=(c='#fff')=>`<div class="logo" style="color:${c}"><span>MUROS</span><small>GYM · FITNESS</small></div>`;
const css=`*{margin:0;box-sizing:border-box}body{width:1080px;height:1350px;font-family:Inter;overflow:hidden;position:relative;background:#111}
.ph{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.sh{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,0) 45%,rgba(0,0,0,.88) 100%)}
.logo{position:absolute;top:56px;left:64px;display:flex;flex-direction:column;line-height:1}
.logo span{font-weight:800;font-size:44px;letter-spacing:6px}.logo small{font-weight:600;font-size:15px;letter-spacing:5px;margin-top:6px;opacity:.85}
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
 slide('a66116d6-image.jpg','30% 50%','Pilates Mat','Moverte bien<br>también es<br><em>entrenar.</em>','Fuerza, postura y calma en una misma clase.',1),
 slide('d91c22ae-image.jpg','62% 50%','Soltá','Bajá un cambio.<br><em>Respirá.</em>','Descomprimí la espalda y liberá la tensión del día.',2),
 slide('5d1d983c-image.jpg','50% 40%','Acompañamiento real','Te corregimos<br><em>uno a uno.</em>','Profes atentas a tu postura para que cada ejercicio te haga bien.',3),
 slide('cfe8f922-image.jpg','25% 50%','Movilidad','Más flexible,<br>más <em>liviano.</em>','Ganás rango de movimiento sin forzar, a tu ritmo.',4),
 slide('8566e071-image.jpg','35% 50%','Para vos','Arrancás desde<br><em>donde estás.</em>','No importa tu edad ni tu nivel. Adaptamos cada movimiento a tu cuerpo.',5),
 slide('01876715-image.jpg','50% 45%','Entrenamiento consciente','Cada movimiento<br>con <em>intención.</em>','En Muros no entrenamos en piloto automático: escuchamos al cuerpo.',6),
 `<html><head><style>${css}
 body{background:${Y}}.c{position:absolute;inset:0;padding:64px;display:flex;flex-direction:column;justify-content:center;color:#111}
 .c h1{font-size:110px}.c .k{font-size:30px;letter-spacing:5px;font-weight:700;margin-bottom:24px}
 .box{margin-top:60px;background:#111;color:#fff;padding:44px 48px;border-radius:6px}
 .row{font-size:40px;font-weight:700;display:flex;gap:22px;align-items:center}.row+.row{margin-top:26px}
 .row b{color:${Y};font-size:24px;letter-spacing:3px;width:190px;font-weight:800}
 .cta{margin-top:56px;font-size:38px;font-weight:800}</style></head><body>${logo('#111')}<div class="num" style="color:#111">07/07</div>
 <div class="c"><div class="k">PILATES MAT · MUROS</div><h1>Tu primera<br>clase te<br>espera.</h1>
 <div class="box"><div class="row"><b>DIRECCIÓN</b>Av. Mitre 926, Campana</div><div class="row"><b>WHATSAPP</b>3489 588703</div></div>
 <div class="cta">Escribinos y reservá tu lugar →</div></div></body></html>`];
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1350}});
for(let i=0;i<slides.length;i++){await pg.setContent(slides[i],{waitUntil:'load'});await pg.screenshot({path:`${OUT}slide-0${i+1}.png`});}
await b.close();})();
