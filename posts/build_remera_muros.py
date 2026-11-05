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
shirt.thumbnail((850,850),Image.LANCZOS)

img=Image.new("RGBA",(W,H),Y+(255,))
d=ImageDraw.Draw(img)
# soft shadow under the shirt
sx=(W-shirt.width)//2; sy=285
sh=Image.new("RGBA",(W,H),(0,0,0,0))
sh.paste((0,0,0,110),(sx+18,sy+28),shirt.split()[3])
img=Image.alpha_composite(img,sh.filter(ImageFilter.GaussianBlur(22)))
img.alpha_composite(shirt,(sx,sy))
d=ImageDraw.Draw(img)

d.rounded_rectangle((60,52,60+190,52+46),radius=23,fill=K)
d.text((155,75),"NUEVA",font=F("Inter-ExtraBold",24),fill=Y,anchor="mm")
d.text((60,112),"REMERA OFICIAL",font=F("Inter-ExtraBold",80),fill=K)
d.text((62,206),"Entrená con los colores de Muros",font=F("Inter-SemiBold",36),fill=(40,40,40))

# bottom band
d.rectangle((0,1150,W,H),fill=K)
d.text((60,1180),"Consultá talles y precio",font=F("Inter-ExtraBold",44),fill="white")
d.text((60,1245),"WhatsApp 3489 588703",font=F("Inter-ExtraBold",34),fill=Y)
d.text((60,1293),"Av. Mitre 926, Campana",font=F("Inter-Medium",28),fill=(200,200,200))
logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((250,140),Image.LANCZOS)
img.alpha_composite(logo,(W-60-logo.width,1250-logo.height//2))
img.convert("RGB").save(os.path.join(here,"remera-muros-venta.png"),quality=95)
