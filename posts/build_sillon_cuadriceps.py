from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1350
src=Image.open("/root/.claude/uploads/4306f732-d120-550e-99c9-b9fa846f5f30/6d3ae982-image.jpg").convert("RGB")
s=W/src.width
img=src.resize((W,round(src.height*s)),Image.LANCZOS)
DY=200
K=src.width/1500  # marks below are measured on a 1500px-wide preview
TOP=round(560*K*s)
base=Image.new("RGB",(W,H),(10,10,12)); base.paste(img.crop((0,TOP,W,TOP+H-DY)),(0,DY)); img=base
def P(x,y): return (round(x*K*s), round(y*K*s)-TOP+DY)
# gradients
ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
for y in range(H):
    a=0
    if y<235: a=255
    elif y<345: a=int(255*(1-(y-235)/110)**1.5)
    if y>820: a=max(a,int(248*min(1,(y-820)/200)))
    d.line([(0,y),(W,y)],fill=(10,10,12,a))
img=Image.alpha_composite(img.convert("RGBA"),ov)
d=ImageDraw.Draw(img)
Y=(255,196,0)
F=lambda n,sz: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/{n}.otf",sz)
black=F("Inter-Black",84) if __import__("os").path.exists("/usr/share/fonts/opentype/inter/Inter-Black.otf") else F("Inter-ExtraBold",84)
# header
d.rounded_rectangle((60,52,330,96),radius=22,fill=Y)
d.text((195,74),"TÉCNICA CORRECTA",font=F("Inter-ExtraBold",24),fill=(15,15,15),anchor="mm")
title="SILLÓN DE CUÁDRICEPS"; sz=84
while d.textlength(title,font=black)>760:
    sz-=2; black=black.font_variant(size=sz)
d.text((60,112+(84-sz)//2),title,font=black,fill="white")
d.text((62,222),"4 claves para piernas fuertes (y rodillas cuidadas)",font=F("Inter-SemiBold",33),fill=(235,235,235))
# markers
marks=[(1,P(790,1200)),(2,P(330,1130)),(3,P(1095,1120)),(4,P(1075,1430))]
for n,(x,y) in marks:
    r=30
    d.ellipse((x-r-5,y-r-5,x+r+5,y+r+5),fill=(15,15,15))
    d.ellipse((x-r,y-r,x+r,y+r),fill=Y)
    d.text((x,y+1),str(n),font=F("Inter-ExtraBold",34),fill=(15,15,15),anchor="mm")
tips=[("Rodilla en el eje","Alineada con el eje de giro: ajustá el respaldo."),
      ("Rodillo al tobillo","Justo arriba del empeine, no en la canilla."),
      ("Espalda apoyada","Cadera pegada al asiento, sin despegarte."),
      ("Agarrate y controlá","Subí en 1 seg, pausa arriba, bajá en 3.")]
y0=1000
for i,(t,sub) in enumerate(tips):
    col=i%2; row=i//2
    x=60+col*500; y=y0+row*130
    d.rounded_rectangle((x,y,x+56,y+56),radius=14,fill=Y)
    d.text((x+28,y+29),str(i+1),font=F("Inter-ExtraBold",32),fill=(15,15,15),anchor="mm")
    d.text((x+74,y-2),t,font=F("Inter-ExtraBold",36),fill="white")
    # wrap sub
    f=F("Inter-Medium",26); words=sub.split(); lines=[""]
    for w in words:
        tst=(lines[-1]+" "+w).strip()
        if d.textlength(tst,font=f)>370: lines.append(w)
        else: lines[-1]=tst
    for j,l in enumerate(lines):
        d.text((x+74,y+48+j*34),l,font=f,fill=(205,205,205))
d.line((60,1268,W-60,1268),fill=(70,70,70),width=2)
d.text((60,1290),"Guardalo para tu próximo día de piernas 💪".replace(" 💪",""),font=F("Inter-SemiBold",28),fill=(230,230,230))
d.text((W-60,1290),"JS PERSONAL TRAINER",font=F("Inter-ExtraBold",26),fill=(214,170,72),anchor="ra")
logo=Image.open(__import__("os").path.join(__import__("os").path.dirname(__file__),"logo-js.png")).convert("RGBA")
logo.thumbnail((190,190),Image.LANCZOS)
img.alpha_composite(logo,(W-45-logo.width,22))
img.convert("RGB").save("/home/user/PEPI/posts/sillon-cuadriceps-post.png",quality=95)
