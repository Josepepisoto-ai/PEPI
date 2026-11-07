from PIL import Image, ImageDraw, ImageFont
import os
here=os.path.dirname(os.path.abspath(__file__))
W,H=1080,1350
Y=(249,235,30); K=(14,14,14); C=(32,32,32)
F=lambda n,sz: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/{n}.otf",sz)
img=Image.new("RGBA",(W,H),K+(255,))
d=ImageDraw.Draw(img)

logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((430,250),Image.LANCZOS)
img.alpha_composite(logo,((W-logo.width)//2,70))

d.rounded_rectangle((W//2-170,360,W//2+170,416),radius=28,fill=Y)
d.text((W//2,388),"AVISO IMPORTANTE",font=F("Inter-ExtraBold",28),fill=K,anchor="mm")
d.text((W//2,470),"Horarios por feriado",font=F("Inter-ExtraBold",56),fill="white",anchor="mm")

def card(y,day,status,line1,line2,closed):
    d.rounded_rectangle((60,y,W-60,y+250),radius=28,fill=C)
    d.rounded_rectangle((60,y,72,y+250),radius=6,fill=(225,40,45) if closed else Y)
    d.text((110,y+38),day,font=F("Inter-ExtraBold",64),fill="white")
    tag_f=F("Inter-ExtraBold",38); tw=d.textlength(status,font=tag_f)+56
    d.rounded_rectangle((W-100-tw,y+42,W-100,y+108),radius=33,fill=(225,40,45) if closed else Y)
    d.text((W-100-tw/2,y+76),status,font=tag_f,fill="white" if closed else K,anchor="mm")
    d.text((110,y+130),line1,font=F("Inter-ExtraBold",46),fill=Y if not closed else (235,235,235))
    d.text((110,y+190),line2,font=F("Inter-Medium",32),fill=(200,200,200))

card(540,"LUNES","CERRADO","Feriado nacional","El gimnasio permanecerá cerrado.",True)
card(830,"MIÉRCOLES","ABIERTO","De 7:00 a 21:30 hs","Gimnasio y sala de entrenamiento grupal.",False)

d.rectangle((0,1140,W,H),fill=Y)
d.text((W//2,1200),"WhatsApp 3489 588703",font=F("Inter-ExtraBold",52),fill=K,anchor="mm")
d.text((W//2,1268),"Av. Mitre 926, Campana",font=F("Inter-SemiBold",36),fill=K,anchor="mm")
img.convert("RGB").save(os.path.join(here,"aviso-feriado-muros.png"),quality=95)
