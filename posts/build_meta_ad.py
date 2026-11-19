from PIL import Image, ImageDraw, ImageFont
import os
W,H=1080,1350
src=Image.open("/root/.claude/uploads/4306f732-d120-550e-99c9-b9fa846f5f30/99858806-image.jpg").convert("RGB")
s=W/src.width
img=src.resize((W,round(src.height*s)),Image.LANCZOS)
img=img.crop((0,30,W,30+H)).convert("RGBA")
# gradients: light at top for the logo, strong at bottom for the copy
ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
for y in range(H):
    a=0
    if y<230: a=int(150*(1-y/230))
    if y>760: a=max(a,int(240*min(1,(y-760)/330)))
    d.line([(0,y),(W,y)],fill=(10,10,12,a))
img=Image.alpha_composite(img,ov)
d=ImageDraw.Draw(img)
Y=(255,196,0); G=(214,170,72)
F=lambda n,sz: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/{n}.otf",sz)
logo=Image.open(os.path.join(os.path.dirname(__file__),"logo-js.png")).convert("RGBA")
logo.thumbnail((170,170),Image.LANCZOS)
img.alpha_composite(logo,(40,30))
# copy
d.text((60,1000),"Entrená con un plan",font=F("Inter-ExtraBold",70),fill="white")
d.text((60,1078),"hecho para vos",font=F("Inter-ExtraBold",70),fill=Y)
d.text((62,1170),"Fuerza · Técnica · Seguimiento personalizado",font=F("Inter-SemiBold",31),fill=(225,225,225))
# CTA
f=F("Inter-ExtraBold",30); label="ESCRIBIME Y EMPEZÁ HOY  →"
bw=d.textlength(label,font=f)+64
d.rounded_rectangle((60,1238,60+bw,1308),radius=35,fill=Y)
d.text((60+bw/2,1274),label,font=f,fill=(15,15,15),anchor="mm")
fh=F("Inter-ExtraBold",26); hd="@pf_jose_pepi_soto"
d.text((W-60,1274),hd,font=fh,fill=G,anchor="rm")
hx=W-60-d.textlength(hd,font=fh); ix=hx-42; iy=1274-15  # Instagram glyph
d.rounded_rectangle((ix,iy,ix+30,iy+30),radius=9,outline=G,width=3)
d.ellipse((ix+8,iy+8,ix+22,iy+22),outline=G,width=3)
d.ellipse((ix+21,iy+4,ix+26,iy+9),fill=G)
img.convert("RGB").save(os.path.join(os.path.dirname(__file__),"meta-ad-entrena.png"),quality=95)
