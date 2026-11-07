from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os, sys
here=os.path.dirname(os.path.abspath(__file__))
STORY="story" in sys.argv[1:]  # python build_fiesta_muros.py story -> 1080x1920
W,H=(1080,1920) if STORY else (1080,1350)
T=210 if STORY else 0          # story safe zones
Y=(249,235,30); K=(10,8,20)
fd=os.path.join(here,"fonts")
ANTON=lambda sz: ImageFont.truetype(os.path.join(fd,"anton-latin-400-normal.woff"),sz)
OSW=lambda sz,w=700: ImageFont.truetype(os.path.join(fd,f"oswald-latin-{w}-normal.woff"),sz)
FR=os.path.join(here,"fiesta-frames")  # frames taken from the party video
fr=lambda t: Image.open(os.path.join(FR,f"f_{t}.jpg")).convert("RGB")

# background: blurred, darkened dance-floor frame with a purple wash
bg=fr("0.3").resize((W,round(1920*W/1080))).crop((0,0,W,H)).filter(ImageFilter.GaussianBlur(26))
bg=ImageEnhance.Brightness(bg).enhance(0.45)
img=Image.alpha_composite(bg.convert("RGBA"),Image.new("RGBA",(W,H),(60,20,110,90)))
ov=Image.new("RGBA",(W,H)); od=ImageDraw.Draw(ov)
for y in range(H):
    od.line([(0,y),(W,y)],fill=(8,6,18,int(200*max(0,(y-H*0.55)/(H*0.45)))))
img=Image.alpha_composite(img,ov)
d=ImageDraw.Draw(img)

logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((300,170),Image.LANCZOS)
img.alpha_composite(logo,((W-logo.width)//2,T+30))
d=ImageDraw.Draw(img)

y=T+232
f=OSW(34); bw=d.textlength("DESPEDIDA DE",font=f)+50
d.rectangle((W//2-bw/2,y,W//2+bw/2,y+56),fill=Y)
d.text((W//2,y+28),"DESPEDIDA DE",font=f,fill=K,anchor="mm")
d.text((W//2,y+150),"FIN DE AÑO 2026",font=ANTON(150),fill="white",anchor="mm")

# three party photos, cropped clear of the video's text overlays
crops=[("0.3",(0,200,600,800),-6),("13.5",(500,220,1080,800),2),("16.5",(420,380,1080,1040),6)]
py=y+(300 if STORY else 250); size=270 if not STORY else 320
xs=[W//2-size-20,W//2,W//2+size+20]
for (t,box,ang),cx in zip(crops,xs):
    ph=fr(t).crop(box).resize((size,size),Image.LANCZOS)
    card=Image.new("RGBA",(size+20,size+20),(255,255,255,255)); card.paste(ph,(10,10))
    card=card.rotate(ang,expand=True,resample=Image.BICUBIC)
    sh=Image.new("RGBA",card.size,(0,0,0,0)); sh.paste((0,0,0,140),(0,0),card.split()[3])
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)),(cx-card.width//2+8,py+12))
    img.alpha_composite(card,(cx-card.width//2,py))
d=ImageDraw.Draw(img)

y=py+size+(90 if STORY else 100)
d.text((W//2,y),"VIERNES 27 DE NOVIEMBRE",font=ANTON(84),fill=Y,anchor="mm")
d.text((W//2,y+90),"21:30 HS",font=ANTON(76),fill="white",anchor="mm")
d.text((W//2,y+165),"PIZZA LIBRE  ·  ANIMACIÓN  ·  SHOW EN VIVO  ·  SORTEOS",font=OSW(36,500),fill="white",anchor="mm")

y=y+(235 if STORY else 225)
# price box + call to action, side by side
f=ANTON(50); pt="TARJETA $30.000"; ct="RESERVÁ TU ENTRADA"
pw=d.textlength(pt,font=f)+60; cw=d.textlength(ct,font=f)+60; gap=24
x0=(W-pw-cw-gap)/2
d.rectangle((x0,y,x0+pw,y+84),outline=Y,width=5)
d.text((x0+pw/2,y+42),pt,font=f,fill="white",anchor="mm")
d.rectangle((x0+pw+gap,y,x0+pw+gap+cw,y+84),fill=Y)
d.text((x0+pw+gap+cw/2,y+42),ct,font=f,fill=K,anchor="mm")
d.text((W//2,y+120),"ANTES DEL 20 DE NOVIEMBRE",font=OSW(34),fill="white",anchor="mm")
d.text((W//2,y+(185 if STORY else 175)),"WHATSAPP 3489-588703  ·  AV. MITRE 926",font=OSW(36),fill=Y,anchor="mm")
img.convert("RGB").save(os.path.join(here,"fiesta-fin-de-ano-muros-historia.png" if STORY else "fiesta-fin-de-ano-muros.png"),quality=95)
