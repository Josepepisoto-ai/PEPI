from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1350
src=Image.open("/root/.claude/uploads/4306f732-d120-550e-99c9-b9fa846f5f30/cbc37213-image.png").convert("RGB")
s=H/src.height
img=src.resize((round(src.width*s),H),Image.LANCZOS)
ox=(img.width-W)//2
DY=200
base=Image.new("RGB",(W,H),(10,10,12)); base.paste(img.crop((ox,0,ox+W,H-DY)),(0,DY)); img=base
def P(x,y): return (round(x*s)-ox, round(y*s)+DY)
# gradients
ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
for y in range(H):
    a=0
    if y<200: a=255
    elif y<330: a=int(255*(1-(y-200)/130)**1.5)
    if y>820: a=max(a,int(248*min(1,(y-820)/200)))
    d.line([(0,y),(W,y)],fill=(10,10,12,a))
img=Image.alpha_composite(img.convert("RGBA"),ov)
d=ImageDraw.Draw(img)
Y=(255,196,0)
F=lambda n,sz: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/{n}.otf",sz)
black=F("Inter-Black",92) if __import__("os").path.exists("/usr/share/fonts/opentype/inter/Inter-Black.otf") else F("Inter-ExtraBold",92)
# header
d.rounded_rectangle((60,52,330,96),radius=22,fill=Y)
d.text((195,74),"TÉCNICA CORRECTA",font=F("Inter-ExtraBold",24),fill=(15,15,15),anchor="mm")
d.text((60,112),"CURL CON BARRA",font=black,fill="white")
d.text((62,222),"4 claves para bíceps más grandes (y codos sanos)",font=F("Inter-SemiBold",33),fill=(235,235,235))
# markers
marks=[(1,P(380,470)),(1,P(865,470)),(2,P(395,620)),(2,P(770,620)),(3,P(600,560))]
for n,(x,y) in marks:
    r=30
    d.ellipse((x-r-5,y-r-5,x+r+5,y+r+5),fill=(15,15,15))
    d.ellipse((x-r,y-r,x+r,y+r),fill=Y)
    d.text((x,y+1),str(n),font=F("Inter-ExtraBold",34),fill=(15,15,15),anchor="mm")
tips=[("Muñecas firmes","Neutras, sin doblarlas hacia atrás."),
      ("Codos pegados","Fijos al costado del cuerpo: no los adelantes."),
      ("Cero balanceo","Tronco quieto. Si te hamacás, bajá el peso."),
      ("Bajá lento","2–3 segundos de bajada, extensión completa.")]
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
d.text((60,1290),"Guardalo para tu próximo día de brazos 💪".replace(" 💪",""),font=F("Inter-SemiBold",28),fill=(230,230,230))
d.text((W-60,1290),"PEPI",font=F("Inter-ExtraBold",30),fill=Y,anchor="ra")
img.convert("RGB").save("/home/user/PEPI/posts/curl-con-barra-post.png",quality=95)
