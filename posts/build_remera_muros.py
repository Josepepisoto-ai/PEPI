from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import os
here=os.path.dirname(os.path.abspath(__file__))
W,H=1080,1350
Y=(249,235,30); K=(15,15,15)
F=lambda n,sz: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/{n}.otf",sz)

# cut the shirt out of its white background: flood the outside from the corners only,
# so the white logo printed on the shirt stays
src=Image.open("/root/.claude/uploads/4306f732-d120-550e-99c9-b9fa846f5f30/0c338f4c-image.jpg").convert("RGB")
m=src.convert("L").point(lambda v:255 if v>200 else 0)
for c in [(0,0),(src.width-1,0),(0,src.height-1),(src.width-1,src.height-1)]:
    ImageDraw.floodfill(m,c,128)
alpha=m.point(lambda v:0 if v==128 else 255).filter(ImageFilter.GaussianBlur(1.2))
shirt=src.convert("RGBA"); shirt.putalpha(alpha)
shirt=shirt.crop(alpha.getbbox())
shirt.thumbnail((800,800),Image.LANCZOS)

import math
img=Image.new("RGBA",(W,H),Y+(255,))
# shirt, shifted left to make room for the price burst
sx=40; sy=262
sh=Image.new("RGBA",(W,H),(0,0,0,0))
sh.paste((0,0,0,110),(sx+18,sy+28),shirt.split()[3])
img=Image.alpha_composite(img,sh.filter(ImageFilter.GaussianBlur(22)))
img.alpha_composite(shirt,(sx,sy))
d=ImageDraw.Draw(img)

# top promo band
d.rectangle((0,0,W,118),fill=K)
d.text((W//2,60),"¡SÚPER PROMO LANZAMIENTO!",font=F("Inter-ExtraBold",58),fill=Y,anchor="mm")
d.text((60,140),"REMERA OFICIAL MUROS",font=F("Inter-ExtraBold",66),fill=K)

# price burst
cx,cy,R=830,640,205
pts=[(cx+(R if i%2==0 else R*0.86)*math.cos(math.pi*i/20-math.pi/2),
      cy+(R if i%2==0 else R*0.86)*math.sin(math.pi*i/20-math.pi/2)) for i in range(40)]
bs=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(bs).polygon([(x+10,y+14) for x,y in pts],fill=(0,0,0,120))
img=Image.alpha_composite(img,bs.filter(ImageFilter.GaussianBlur(10)))
d=ImageDraw.Draw(img)
d.polygon(pts,fill=(225,30,40))
d.ellipse((cx-R*0.8,cy-R*0.8,cx+R*0.8,cy+R*0.8),outline="white",width=4)
d.text((cx,cy-66),"PRECIO",font=F("Inter-ExtraBold",30),fill="white",anchor="mm")
d.text((cx,cy-32),"LANZAMIENTO",font=F("Inter-ExtraBold",28),fill="white",anchor="mm")
d.text((cx,cy+30),"$25.000",font=F("Inter-ExtraBold",62),fill="white",anchor="mm")

# bottom band
d.rectangle((0,1130,W,H),fill=K)
d.text((60,1158),"¡Solo las primeras 30 remeras!",font=F("Inter-ExtraBold",46),fill=Y)
d.text((60,1228),"Pedila por WhatsApp 3489 588703",font=F("Inter-ExtraBold",32),fill="white")
d.text((60,1280),"Av. Mitre 926, Campana",font=F("Inter-Medium",28),fill=(200,200,200))
logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((210,120),Image.LANCZOS)
img.alpha_composite(logo,(W-60-logo.width,1300-logo.height))
img.convert("RGB").save(os.path.join(here,"remera-muros-venta.png"),quality=95)
