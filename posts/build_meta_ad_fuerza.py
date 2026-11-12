from PIL import Image, ImageDraw, ImageFont
import os, sys
STORY="story" in sys.argv[1:]  # python build_meta_ad_fuerza.py story -> 1080x1920
W,H=(1080,1920) if STORY else (1080,1350)
T=250 if STORY else 0      # story top safe zone
D=230 if STORY else 0      # story: copy block moves down, still above the bottom 380px
src=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"fotos","peso-muerto-barra.jpg")).convert("RGB")
if STORY:
    s=H/src.height; img=src.resize((round(src.width*s),H),Image.LANCZOS); ox=(img.width-W)//2
    img=img.crop((ox,0,ox+W,H)).convert("RGBA")
else:
    s=W/src.width
    img=src.resize((W,round(src.height*s)),Image.LANCZOS)
    img=img.crop((0,200,W,200+H)).convert("RGBA")
# gradients: light at top for the logo, strong at bottom for the copy
ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
for y in range(H):
    a=0
    if y<T+300: a=int(200*(1-y/(T+300)))
    if y>760+D: a=max(a,int(240*min(1,(y-760-D)/330)))
    d.line([(0,y),(W,y)],fill=(10,10,12,a))
img=Image.alpha_composite(img,ov)
d=ImageDraw.Draw(img)
Y=(255,196,0); G=(214,170,72)
F=lambda n,sz: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/{n}.otf",sz)
logo=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"logo-js.png")).convert("RGBA")
logo.thumbnail((170,170),Image.LANCZOS)
img.alpha_composite(logo,(40,T+30))
# copy
d.text((60,1000+D),"Ganá fuerza con",font=F("Inter-ExtraBold",70),fill="white")
d.text((60,1078+D),"técnica y método",font=F("Inter-ExtraBold",70),fill=Y)
d.text((62,1170+D),"Plan a tu medida · Corrección en cada serie",font=F("Inter-SemiBold",31),fill=(225,225,225))
# CTA
f=F("Inter-ExtraBold",30); label="ESCRIBIME Y EMPEZÁ HOY  →"
bw=d.textlength(label,font=f)+64
d.rounded_rectangle((60,1238+D,60+bw,1308+D),radius=35,fill=Y)
d.text((60+bw/2,1274+D),label,font=f,fill=(15,15,15),anchor="mm")
fh=F("Inter-ExtraBold",26); hd="@pf_jose_pepi_soto"
d.text((W-60,1274+D),hd,font=fh,fill=G,anchor="rm")
hx=W-60-d.textlength(hd,font=fh); ix=hx-42; iy=1274+D-15  # Instagram glyph
d.rounded_rectangle((ix,iy,ix+30,iy+30),radius=9,outline=G,width=3)
d.ellipse((ix+8,iy+8,ix+22,iy+22),outline=G,width=3)
d.ellipse((ix+21,iy+4,ix+26,iy+9),fill=G)
img.convert("RGB").save(os.path.join(os.path.dirname(__file__),"meta-ad-fuerza-historia.png" if STORY else "meta-ad-fuerza.png"),quality=95)
