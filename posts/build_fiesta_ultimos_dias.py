from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os, sys
here=os.path.dirname(os.path.abspath(__file__))
STORY="story" in sys.argv[1:]  # python build_fiesta_ultimos_dias.py story -> 1080x1920
W,H=(1080,1920) if STORY else (1080,1350)
Y=(249,235,30); K=(10,8,20); BG=(18,10,34)
fd=os.path.join(here,"fonts")
ANTON=lambda sz: ImageFont.truetype(os.path.join(fd,"anton-latin-400-normal.woff"),sz)
OSW=lambda sz,w=700: ImageFont.truetype(os.path.join(fd,f"oswald-latin-{w}-normal.woff"),sz)
fr=lambda t: Image.open(os.path.join(here,"fiesta-frames",f"f_{t}.jpg")).convert("RGB")

img=Image.new("RGBA",(W,H),BG+(255,))
# background: fireworks photo, full bleed, darkened toward the bottom for the copy
HH=900 if STORY else 600   # where the urgency ribbon sits
src=Image.open(os.path.join(here,"fotos","fuegos-artificiales.jpg")).convert("RGB")
sc=max(W/src.width,H/src.height); bgp=src.resize((round(src.width*sc),round(src.height*sc)),Image.LANCZOS)
ox=(bgp.width-W)//2; oy=0 if STORY else round(bgp.height*0.08)
img=bgp.crop((ox,oy,ox+W,oy+H)).convert("RGBA")
ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
for y in range(H):
    a_=0
    if y<260: a_=int(150*(1-y/260))
    g0=HH-120
    if y>g0: a_=max(a_,int(225*min(1,(y-g0)/260)))
    od.line([(0,y),(W,y)],fill=BG+(a_,))
img=Image.alpha_composite(img,ov)
T=210 if STORY else 0
logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((260,150) if STORY else (210,118),Image.LANCZOS)
lx,ly=W-40-logo.width,T+(30 if STORY else 18)
halo=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(halo).ellipse((lx-50,ly-40,lx+logo.width+50,ly+logo.height+40),fill=BG+(200,))
img=Image.alpha_composite(img,halo.filter(ImageFilter.GaussianBlur(30)))  # keeps the logo readable over bright fireworks
img.alpha_composite(logo,(lx,ly))

# urgency ribbon across the bottom of the photo
rb=Image.new("RGBA",(W+200,130),Y+(255,)); rd=ImageDraw.Draw(rb)
rd.text(((W+200)//2,65),"¡QUEDAN POCOS DÍAS PARA ANOTARTE!",font=ANTON(70),fill=K,anchor="mm")
rb=rb.rotate(4,expand=True,resample=Image.BICUBIC)
sh=Image.new("RGBA",rb.size,(0,0,0,0)); sh.paste((0,0,0,150),(0,0),rb.split()[3])
y0=HH-140
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)),(-100,y0+10))
img.alpha_composite(rb,(-100,y0))
d=ImageDraw.Draw(img)

y=HH+(150 if STORY else 110)
d.text((W//2,y),"DESPEDIDA DE",font=OSW(40),fill=Y,anchor="mm")
d.text((W//2,y+95),"FIN DE AÑO 2026",font=ANTON(132),fill="white",anchor="mm")
d.text((W//2,y+215),"VIERNES 27/11  ·  21:30 HS",font=ANTON(76),fill=Y,anchor="mm")
d.text((W//2,y+293),"PIZZA LIBRE  ·  ANIMACIÓN  ·  SHOW EN VIVO  ·  SORTEOS",font=OSW(36,500),fill="white",anchor="mm")

y=y+(380 if STORY else 360)
f=ANTON(52); pt="TARJETA $30.000"; ct="¡ANOTATE YA!"
pw=d.textlength(pt,font=f)+60; cw=d.textlength(ct,font=f)+80; gap=24
x0=(W-pw-cw-gap)/2
d.rectangle((x0,y,x0+pw,y+88),outline=Y,width=5)
d.text((x0+pw/2,y+44),pt,font=f,fill="white",anchor="mm")
d.rectangle((x0+pw+gap,y,x0+pw+gap+cw,y+88),fill=Y)
d.text((x0+pw+gap+cw/2,y+44),ct,font=f,fill=K,anchor="mm")
d.text((W//2,y+150),"WHATSAPP 3489-588703  ·  AV. MITRE 926",font=OSW(38),fill=Y,anchor="mm")
img.convert("RGB").save(os.path.join(here,"fiesta-ultimos-dias-muros-historia.png" if STORY else "fiesta-ultimos-dias-muros.png"),quality=95)
