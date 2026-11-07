from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1350
src=Image.open("/root/.claude/uploads/4306f732-d120-550e-99c9-b9fa846f5f30/003995ae-image.jpg").convert("RGB")
K=src.width/1500  # marks below are measured on a 1500px-wide preview
DY=200; Y0,Y1=270,1760  # preview rows that must fit between the header and the tips
s=(1040-DY)/((Y1-Y0)*K)
fg=src.resize((round(src.width*s),round(src.height*s)),Image.LANCZOS)
OX=(W-fg.width)//2; TOP=round(Y0*K*s)
# blurred, darkened copy fills the sides
bs=W/src.width
bg=src.resize((W,round(src.height*bs)),Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
bg=Image.eval(bg,lambda v:int(v*0.45))
base=Image.new("RGB",(W,H),(10,10,12)); base.paste(bg.crop((0,round(Y0*K*bs),W,round(Y0*K*bs)+H-DY)),(0,DY))
mask=Image.new("L",fg.size,255); md=ImageDraw.Draw(mask)
for i in range(60):
    v=int(255*i/60); md.line([(i,0),(i,fg.height)],fill=v); md.line([(fg.width-1-i,0),(fg.width-1-i,fg.height)],fill=v)
base.paste(fg.crop((0,TOP,fg.width,TOP+H-DY)),(OX,DY),mask.crop((0,TOP,fg.width,TOP+H-DY)))
img=base
def P(x,y): return (round(x*K*s)+OX, round(y*K*s)-TOP+DY)
# gradients
ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
for y in range(H):
    a=0
    if y<235: a=255
    elif y<345: a=int(255*(1-(y-235)/110)**1.5)
    if y>960: a=max(a,int(248*min(1,(y-960)/110)))
    d.line([(0,y),(W,y)],fill=(10,10,12,a))
img=Image.alpha_composite(img.convert("RGBA"),ov)
d=ImageDraw.Draw(img)
Y=(255,196,0)
F=lambda n,sz: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/{n}.otf",sz)
black=F("Inter-Black",84) if __import__("os").path.exists("/usr/share/fonts/opentype/inter/Inter-Black.otf") else F("Inter-ExtraBold",84)
# header
d.rounded_rectangle((60,52,330,96),radius=22,fill=Y)
d.text((195,74),"TÉCNICA CORRECTA",font=F("Inter-ExtraBold",24),fill=(15,15,15),anchor="mm")
title="STEP UP CON BARRA"; sz=84
while d.textlength(title,font=black)>760:
    sz-=2; black=black.font_variant(size=sz)
d.text((60,112+(84-sz)//2),title,font=black,fill="white")
d.text((62,222),"4 claves para glúteos y piernas fuertes",font=F("Inter-SemiBold",33),fill=(235,235,235))
# markers
marks=[(1,P(770,525)),(2,P(760,830)),(3,P(790,1650)),(4,P(835,1330))]
for n,(x,y) in marks:
    r=30
    d.ellipse((x-r-5,y-r-5,x+r+5,y+r+5),fill=(15,15,15))
    d.ellipse((x-r,y-r,x+r,y+r),fill=Y)
    d.text((x,y+1),str(n),font=F("Inter-ExtraBold",34),fill=(15,15,15),anchor="mm")
tips=[("Barra en trapecios","Espalda alta, nunca en el cuello."),
      ("Torso firme","Core apretado, leve inclinación."),
      ("Empujá con el talón","Pie entero arriba del step."),
      ("Rodilla alineada","Sigue la punta del pie.")]
y0=1075
for i,(t,sub) in enumerate(tips):
    col=i%2; row=i//2
    x=60+col*500; y=y0+row*96
    d.rounded_rectangle((x,y,x+56,y+56),radius=14,fill=Y)
    d.text((x+28,y+29),str(i+1),font=F("Inter-ExtraBold",32),fill=(15,15,15),anchor="mm")
    d.text((x+74,y-2),t,font=F("Inter-ExtraBold",36),fill="white")
    # wrap sub
    f=F("Inter-Medium",25); words=sub.split(); lines=[""]
    for w in words:
        tst=(lines[-1]+" "+w).strip()
        if d.textlength(tst,font=f)>410: lines.append(w)
        else: lines[-1]=tst
    for j,l in enumerate(lines):
        d.text((x+74,y+48+j*34),l,font=f,fill=(205,205,205))
d.line((60,1268,W-60,1268),fill=(70,70,70),width=2)
d.text((60,1290),"Guardalo para tu próximo día de piernas 💪".replace(" 💪",""),font=F("Inter-SemiBold",28),fill=(230,230,230))
G=(214,170,72); fh=F("Inter-ExtraBold",28); hx=W-60-d.textlength("@pf_jose_pepi_soto",font=fh)
d.text((W-60,1290),"@pf_jose_pepi_soto",font=fh,fill=G,anchor="ra")
ix=hx-46; iy=1290  # Instagram glyph
d.rounded_rectangle((ix,iy,ix+34,iy+34),radius=10,outline=G,width=3)
d.ellipse((ix+9,iy+9,ix+25,iy+25),outline=G,width=3)
d.ellipse((ix+24,iy+5,ix+29,iy+10),fill=G)
logo=Image.open(__import__("os").path.join(__import__("os").path.dirname(__file__),"logo-js.png")).convert("RGBA")
logo.thumbnail((190,190),Image.LANCZOS)
img.alpha_composite(logo,(W-45-logo.width,22))
img.convert("RGB").save("/home/user/PEPI/posts/step-up-post.png",quality=95)
