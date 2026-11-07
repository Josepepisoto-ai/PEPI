from PIL import Image, ImageDraw, ImageFont
import os
here=os.path.dirname(os.path.abspath(__file__))
W,H=1080,1350
Y=(249,235,30); K=(14,14,14); R=(220,35,40)
fd=os.path.join(here,"fonts")
ANTON=lambda sz: ImageFont.truetype(os.path.join(fd,"anton-latin-400-normal.woff"),sz)
OSW=lambda sz,w=700: ImageFont.truetype(os.path.join(fd,f"oswald-latin-{w}-normal.woff"),sz)

img=Image.new("RGBA",(W,H),Y+(255,))
d=ImageDraw.Draw(img)
# black header with a slanted edge
d.polygon([(0,0),(W,0),(W,300),(0,370)],fill=K)
logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((380,215),Image.LANCZOS)
img.alpha_composite(logo,((W-logo.width)//2,50))
d=ImageDraw.Draw(img)

d.text((W//2,445),"FERIADO NACIONAL",font=ANTON(118),fill=K,anchor="mm")

# LUNES - closed
d.text((70,530),"LUNES",font=ANTON(170),fill=K)
stamp=Image.new("RGBA",(470,170),(0,0,0,0)); sd=ImageDraw.Draw(stamp)
sd.rounded_rectangle((6,6,464,164),radius=18,outline=R,width=10)
sd.text((235,85),"CERRADO",font=ANTON(108),fill=R,anchor="mm")
stamp=stamp.rotate(-8,expand=True,resample=Image.BICUBIC)
img.alpha_composite(stamp,(W-60-stamp.width,545))
d=ImageDraw.Draw(img)

d.line((70,775,W-70,775),fill=K,width=4)

# MIÉRCOLES - open
d.text((70,795),"MIÉRCOLES",font=ANTON(150),fill=K)
d.rectangle((70,990,W-70,1090),fill=K)
d.text((W//2,1040),"ABIERTO DE 7:00 A 21:30 HS",font=ANTON(70),fill=Y,anchor="mm")
d.text((W//2,1128),"GIMNASIO  +  SALA DE ENTRENAMIENTO GRUPAL",font=OSW(40),fill=K,anchor="mm")

d.rectangle((0,1190,W,H),fill=K)
d.text((W//2,1238),"WHATSAPP 3489 588703",font=OSW(52),fill=Y,anchor="mm")
d.text((W//2,1300),"AV. MITRE 926 · CAMPANA",font=OSW(36,500),fill="white",anchor="mm")
img.convert("RGB").save(os.path.join(here,"aviso-feriado-muros.png"),quality=95)
