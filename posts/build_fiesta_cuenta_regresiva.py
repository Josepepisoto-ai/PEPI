"""Countdown stories for the Muros end-of-year party (Fri 27/11).
python build_fiesta_cuenta_regresiva.py -> fiesta-cuenta-regresiva/faltan-*.png (1080x1920)"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
here=os.path.dirname(os.path.abspath(__file__))
out=os.path.join(here,"fiesta-cuenta-regresiva"); os.makedirs(out,exist_ok=True)
W,H=1080,1920
T,B=250,1920-380   # story safe zones
Y=(249,235,30); K=(10,8,20); BG=(18,10,34)
fd=os.path.join(here,"fonts")
ANTON=lambda sz: ImageFont.truetype(os.path.join(fd,"anton-latin-400-normal.woff"),sz)
OSW=lambda sz,w=700: ImageFont.truetype(os.path.join(fd,f"oswald-latin-{w}-normal.woff"),sz)

src=Image.open(os.path.join(here,"fotos","fuegos-artificiales.jpg")).convert("RGB")
sc=max(W/src.width,H/src.height); bgp=src.resize((round(src.width*sc),round(src.height*sc)),Image.LANCZOS)
ox=(bgp.width-W)//2
base=bgp.crop((ox,0,ox+W,H)).convert("RGBA")
ov=Image.new("RGBA",(W,H),BG+(150,))   # darken evenly so the big number reads anywhere
base=Image.alpha_composite(base,ov)
logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((300,170),Image.LANCZOS)

def ribbon(text,y,size=64,angle=-3):
    f=ANTON(size); tmp=ImageDraw.Draw(Image.new("RGBA",(1,1)))
    w=int(tmp.textlength(text,font=f))+90
    rb=Image.new("RGBA",(w,size+50),Y+(255,)); ImageDraw.Draw(rb).text((w//2,(size+50)//2),text,font=f,fill=K,anchor="mm")
    return rb.rotate(angle,expand=True,resample=Image.BICUBIC),y

# (file, top line, big text, bottom line, ribbon, extra line)
days=[
 ("faltan-4","FALTAN","4","DÍAS","INSCRIPCIÓN HASTA EL MIÉRCOLES 25/11","Tarjeta $30.000 · WhatsApp 3489-588703"),
 ("faltan-3","FALTAN","3","DÍAS","INSCRIPCIÓN HASTA EL MIÉRCOLES 25/11","Tarjeta $30.000 · WhatsApp 3489-588703"),
 ("faltan-2","FALTAN","2","DÍAS","¡HOY CIERRA LA INSCRIPCIÓN!","Tarjeta $30.000 · WhatsApp 3489-588703"),
 ("falta-1","FALTA","1","DÍA","¡ES MAÑANA!","Acordate de traer tu bebida 🥤"),
 ("es-hoy","","¡HOY!","","¡NOS VEMOS A LAS 21:30!","Acordate de traer tu bebida 🥤"),
]
for name,top,big,bottom,rib,extra in days:
    img=base.copy(); d=ImageDraw.Draw(img)
    img.alpha_composite(logo,((W-logo.width)//2,T+10)); d=ImageDraw.Draw(img)
    d.text((W//2,T+250),"DESPEDIDA DE FIN DE AÑO 2026",font=OSW(46),fill="white",anchor="mm")
    if top: d.text((W//2,T+345),top,font=ANTON(100),fill="white",anchor="mm")
    bf=ANTON(460 if len(big)==1 else 300)
    cy=T+610
    # soft glow behind the number
    gl=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(gl).text((W//2,cy),big,font=bf,fill=Y+(160,),anchor="mm")
    img=Image.alpha_composite(img,gl.filter(ImageFilter.GaussianBlur(28))); d=ImageDraw.Draw(img)
    d.text((W//2,cy),big,font=bf,fill=Y,anchor="mm")
    if bottom: d.text((W//2,T+880),bottom,font=ANTON(100),fill="white",anchor="mm")
    rb,_=ribbon(rib,0)
    img.alpha_composite(rb,((W-rb.width)//2,T+975)); d=ImageDraw.Draw(img)
    d.text((W//2,B-130),"VIERNES 27/11 · 21:30 HS · AV. MITRE 926",font=OSW(42),fill=Y,anchor="mm")
    ef=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",34)
    d.text((W//2,B-68),extra.replace(" 🥤",""),font=ef,fill="white",anchor="mm")
    img.convert("RGB").save(os.path.join(out,name+".png"),quality=95)
print("ok")
