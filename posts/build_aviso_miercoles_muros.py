from PIL import Image, ImageDraw, ImageFont
import os, sys
here=os.path.dirname(os.path.abspath(__file__))
STORY="story" in sys.argv[1:]  # python build_aviso_miercoles_muros.py story -> 1080x1920
W,H=(1080,1920) if STORY else (1080,1350)
S=200 if STORY else 0   # story: push content below the top safe zone
Y=(249,235,30); K=(14,14,14)
fd=os.path.join(here,"fonts")
ANTON=lambda sz: ImageFont.truetype(os.path.join(fd,"anton-latin-400-normal.woff"),sz)
OSW=lambda sz,w=700: ImageFont.truetype(os.path.join(fd,f"oswald-latin-{w}-normal.woff"),sz)

img=Image.new("RGBA",(W,H),Y+(255,))
d=ImageDraw.Draw(img)
d.polygon([(0,0),(W,0),(W,300+S),(0,370+S)],fill=K)
logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((380,215),Image.LANCZOS)
img.alpha_composite(logo,((W-logo.width)//2,50+(240 if STORY else 0)))
d=ImageDraw.Draw(img)

d.text((W//2,440+S),"ESTAMOS ABIERTOS",font=ANTON(112),fill=K,anchor="mm")
# day + date
d.text((70,520+S),"MIÉRCOLES",font=ANTON(150),fill=K)
dt=ANTON(150); dw=d.textlength("11/11",font=dt)
d.rectangle((W-70-dw-40,540+S,W-70,700+S),fill=K)
d.text((W-70-dw/2-20,620+S),"11/11",font=dt,fill=Y,anchor="mm")

d.rectangle((70,740+S,W-70,860+S),fill=K)
d.text((W//2,800+S),"DE 7:00 A 21:30 HS",font=ANTON(84),fill=Y,anchor="mm")

d.line((70,905+S,W-70,905+S),fill=K,width=4)
d.text((W//2,975+S),"CLASES GRUPALES",font=ANTON(92),fill=K,anchor="mm")
d.text((W//2,1065+S),"TODAS EN SU HORARIO DE SIEMPRE",font=OSW(46),fill=K,anchor="mm")
d.text((W//2,1122+S),"(el mismo de todos los miércoles)",font=OSW(36,500),fill=K,anchor="mm")

d.rectangle((0,1190+S,W,H),fill=K)
d.text((W//2,1238+S),"WHATSAPP 3489 588703",font=OSW(52),fill=Y,anchor="mm")
d.text((W//2,1300+S),"AV. MITRE 926 · CAMPANA",font=OSW(36,500),fill="white",anchor="mm")
img.convert("RGB").save(os.path.join(here,"aviso-miercoles-muros-historia.png" if STORY else "aviso-miercoles-muros.png"),quality=95)
