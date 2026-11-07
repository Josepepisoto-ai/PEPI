from PIL import Image, ImageDraw, ImageFont
import os
here=os.path.dirname(os.path.abspath(__file__))
import sys
STORY="story" in sys.argv[1:]  # python build_aviso_feriado_muros.py story -> 1080x1920
W,H=(1080,1920) if STORY else (1080,1350)
S=200 if STORY else 0   # story: push content below the 250px top safe zone
Y=(249,235,30); K=(14,14,14); R=(220,35,40)
fd=os.path.join(here,"fonts")
ANTON=lambda sz: ImageFont.truetype(os.path.join(fd,"anton-latin-400-normal.woff"),sz)
OSW=lambda sz,w=700: ImageFont.truetype(os.path.join(fd,f"oswald-latin-{w}-normal.woff"),sz)

img=Image.new("RGBA",(W,H),Y+(255,))
d=ImageDraw.Draw(img)
# black header with a slanted edge
d.polygon([(0,0),(W,0),(W,300+S),(0,370+S)],fill=K)
logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((380,215),Image.LANCZOS)
img.alpha_composite(logo,((W-logo.width)//2,50+(240 if STORY else 0)))
d=ImageDraw.Draw(img)

d.text((W//2,445+S),"FERIADO NACIONAL",font=ANTON(118),fill=K,anchor="mm")

# LUNES - closed
d.text((70,530+S),"LUNES",font=ANTON(170),fill=K)
stamp=Image.new("RGBA",(470,170),(0,0,0,0)); sd=ImageDraw.Draw(stamp)
sd.rounded_rectangle((6,6,464,164),radius=18,outline=R,width=10)
sd.text((235,85),"CERRADO",font=ANTON(108),fill=R,anchor="mm")
stamp=stamp.rotate(-8,expand=True,resample=Image.BICUBIC)
img.alpha_composite(stamp,(W-60-stamp.width,545+S))
d=ImageDraw.Draw(img)

d.line((70,775+S,W-70,775+S),fill=K,width=4)

# MIÉRCOLES - open
d.text((70,795+S),"MIÉRCOLES",font=ANTON(150),fill=K)
d.rectangle((70,990+S,W-70,1090+S),fill=K)
d.text((W//2,1040+S),"ABIERTO DE 7:00 A 21:30 HS",font=ANTON(70),fill=Y,anchor="mm")
d.text((W//2,1128+S),"GIMNASIO  +  SALA DE ENTRENAMIENTO GRUPAL",font=OSW(40),fill=K,anchor="mm")

d.rectangle((0,1190+S,W,H),fill=K)
d.text((W//2,1238+S),"WHATSAPP 3489 588703",font=OSW(52),fill=Y,anchor="mm")
d.text((W//2,1300+S),"AV. MITRE 926 · CAMPANA",font=OSW(36,500),fill="white",anchor="mm")
img.convert("RGB").save(os.path.join(here,"aviso-feriado-muros-historia.png" if STORY else "aviso-feriado-muros.png"),quality=95)
