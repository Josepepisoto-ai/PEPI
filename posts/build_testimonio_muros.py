from PIL import Image, ImageDraw, ImageFont
import os
# Completar con el testimonio real y el nombre que la alumna autorizó
QUOTE="[Acá va el testimonio de la alumna, con sus propias palabras]"
AUTHOR="[Nombre de la alumna]"
CLASS="Pilates Mat con la profe Gaby"
OUT="testimonio-muros.png"

W,H=1080,1350
here=os.path.dirname(os.path.abspath(__file__))
src=Image.open("/root/.claude/uploads/4306f732-d120-550e-99c9-b9fa846f5f30/bd388ed1-image.jpg").convert("RGB")
s=W/src.width
img=src.resize((W,round(src.height*s)),Image.LANCZOS).crop((0,0,W,H)).convert("RGBA")
ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
for y in range(H):
    a=0
    if y<220: a=int(170*(1-y/220))
    if y>760: a=max(a,int(245*min(1,(y-760)/240)))
    d.line([(0,y),(W,y)],fill=(12,12,12,a))
img=Image.alpha_composite(img,ov)
d=ImageDraw.Draw(img)
Y=(249,235,30)
F=lambda n,sz: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/{n}.otf",sz)
logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((230,130),Image.LANCZOS)
img.alpha_composite(logo,(W-50-logo.width,36))
d.rounded_rectangle((50,48,50+250,48+46),radius=23,fill=Y)
d.text((175,71),"LO QUE DICEN",font=F("Inter-ExtraBold",24),fill=(15,15,15),anchor="mm")
# quote
d.text((52,880),"“",font=F("Inter-Black",190) if os.path.exists("/usr/share/fonts/opentype/inter/Inter-Black.otf") else F("Inter-ExtraBold",190),fill=Y)
fq=F("Inter-SemiBoldItalic",44); words=QUOTE.split(); lines=[""]
for w in words:
    t=(lines[-1]+" "+w).strip()
    if d.textlength(t,font=fq)>W-120: lines.append(w)
    else: lines[-1]=t
y=1040-max(0,len(lines)-3)*56
for l in lines:
    d.text((60,y),l,font=fq,fill="white"); y+=56
y+=18
d.line((60,y+20,110,y+20),fill=Y,width=4)
d.text((126,y),AUTHOR,font=F("Inter-ExtraBold",32),fill=Y)
d.text((126,y+42),CLASS,font=F("Inter-Medium",27),fill=(210,210,210))
img.convert("RGB").save(os.path.join(here,OUT),quality=95)
