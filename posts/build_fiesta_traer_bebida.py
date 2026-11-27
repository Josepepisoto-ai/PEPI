"""Party-day reminder card: bring your own drink and glass.
python build_fiesta_traer_bebida.py         -> 1080x1080 (WhatsApp)
python build_fiesta_traer_bebida.py story   -> 1080x1920 (Instagram story)"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys
here=os.path.dirname(os.path.abspath(__file__))
STORY="story" in sys.argv[1:]
W,H=(1080,1920) if STORY else (1080,1080)
S=450 if STORY else 0      # story: content block starts lower, clear of the safe zones
Y=(249,235,30); K=(10,8,20); BG=(18,10,34); R=(220,35,40)
fd=os.path.join(here,"fonts")
ANTON=lambda sz: ImageFont.truetype(os.path.join(fd,"anton-latin-400-normal.woff"),sz)
OSW=lambda sz,w=700: ImageFont.truetype(os.path.join(fd,f"oswald-latin-{w}-normal.woff"),sz)

src=Image.open(os.path.join(here,"fotos","fuegos-artificiales.jpg")).convert("RGB")
sc=max(W/src.width,H/src.height); bgp=src.resize((round(src.width*sc),round(src.height*sc)),Image.LANCZOS)
ox=(bgp.width-W)//2; oy=0 if STORY else round(bgp.height*0.1)
img=bgp.crop((ox,oy,ox+W,oy+H)).convert("RGBA")
img=Image.alpha_composite(img,Image.new("RGBA",(W,H),BG+(165,)))
logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((260,150),Image.LANCZOS)
img.alpha_composite(logo,((W-logo.width)//2,S-(90 if STORY else -25)))
d=ImageDraw.Draw(img)

y=S+(130 if STORY else 245)
d.text((W//2,y),"¡HOY ES LA FIESTA!",font=ANTON(92),fill="white",anchor="mm")
d.text((W//2,y+85),"VIERNES 27/11 · 21:30 HS · AV. MITRE 926",font=OSW(40),fill=Y,anchor="mm")

# warning stamp + the key message, as big as it fits
y+=160
f=OSW(44); t="⚠  MUY IMPORTANTE  ⚠".replace("⚠","!")
tw=d.textlength(t,font=f)+60
d.rectangle((W//2-tw/2,y,W//2+tw/2,y+66),fill=R)
d.text((W//2,y+33),t,font=f,fill="white",anchor="mm")
y+=100
box=(60,y,W-60,y+(400 if STORY else 340))
gl=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(gl).rectangle(box,fill=Y+(150,))
img=Image.alpha_composite(img,gl.filter(ImageFilter.GaussianBlur(24))); d=ImageDraw.Draw(img)
d.rectangle(box,fill=Y)
cy=(box[1]+box[3])//2
d.text((W//2,cy-(95 if STORY else 80)),"TRAÉ TU BEBIDA",font=ANTON(130 if STORY else 112),fill=K,anchor="mm")
d.text((W//2,cy+(70 if STORY else 60)),"Y TU VASO",font=ANTON(150 if STORY else 128),fill=K,anchor="mm")
y=box[3]+(60 if STORY else 50)
d.text((W//2,y),"La bebida y los vasos NO están incluidos",font=OSW(42,500),fill="white",anchor="mm")
img.convert("RGB").save(os.path.join(here,"fiesta-traer-bebida-historia.png" if STORY else "fiesta-traer-bebida-whatsapp.png"),quality=95)
