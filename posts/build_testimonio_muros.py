from PIL import Image, ImageDraw, ImageFont
import os
# Completar con el testimonio real y el nombre que la alumna autorizó
QUOTE="Las mejores clases de elongación y fuerza."
AUTHOR="Silvia, 54 años"
CLASS="Alumna de la profe Gaby"
import sys
STORY="story" in sys.argv[1:]  # python build_testimonio_muros.py story -> 1080x1920
OUT="testimonio-muros-historia.png" if STORY else "testimonio-muros.png"

W,H=(1080,1920) if STORY else (1080,1350)
TOP=250 if STORY else 0      # Instagram story safe zones
BOT=1920-380 if STORY else 1350
here=os.path.dirname(os.path.abspath(__file__))
src=Image.open("/root/.claude/uploads/4306f732-d120-550e-99c9-b9fa846f5f30/bd388ed1-image.jpg").convert("RGB")
if STORY:
    s=H/src.height; ox=round(192*s)  # keep Gaby and the student in frame
else:
    s=W/src.width; ox=0
img=src.resize((round(src.width*s),round(src.height*s)),Image.LANCZOS).crop((ox,0,ox+W,H)).convert("RGBA")
ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
for y in range(H):
    a=0
    if y<TOP+220: a=int(170*(1-y/(TOP+220)))
    G0=BOT-(480 if STORY else 590)
    if y>G0: a=max(a,int(245*min(1,(y-G0)/240)))
    d.line([(0,y),(W,y)],fill=(12,12,12,a))
img=Image.alpha_composite(img,ov)
d=ImageDraw.Draw(img)
Y=(249,235,30)
F=lambda n,sz: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/{n}.otf",sz)
logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((230,130),Image.LANCZOS)
img.alpha_composite(logo,(W-50-logo.width,TOP+36))
d.rounded_rectangle((50,TOP+48,50+250,TOP+48+46),radius=23,fill=Y)
d.text((175,TOP+71),"LO QUE DICEN",font=F("Inter-ExtraBold",24),fill=(15,15,15),anchor="mm")
# quote
fq=F("Inter-SemiBoldItalic",60 if len(QUOTE)<70 else 44); words=QUOTE.split(); lines=[""]
for w in words:
    t=(lines[-1]+" "+w).strip()
    if d.textlength(t,font=fq)>W-120: lines.append(w)
    else: lines[-1]=t
lh=fq.size+14; y=BOT-(95 if STORY else 145)-len(lines)*lh  # bottom-anchored so short quotes sit low
qf=F("Inter-Black",190) if os.path.exists("/usr/share/fonts/opentype/inter/Inter-Black.otf") else F("Inter-ExtraBold",190)
d.text((52,y-165),"“",font=qf,fill=Y)
for l in lines:
    d.text((60,y),l,font=fq,fill="white"); y+=lh
y+=18
d.line((60,y+20,110,y+20),fill=Y,width=4)
d.text((126,y),AUTHOR,font=F("Inter-ExtraBold",32),fill=Y)
d.text((126,y+42),CLASS,font=F("Inter-Medium",27),fill=(210,210,210))
if STORY:
    d.text((W//2,BOT+70),"Muros Gym Fitness · Av. Mitre 926, Campana",font=F("Inter-SemiBold",28),fill=(200,200,200),anchor="mm")
img.convert("RGB").save(os.path.join(here,OUT),quality=95)
