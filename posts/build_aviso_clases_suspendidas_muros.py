from PIL import Image, ImageDraw, ImageFont
import os, sys
here=os.path.dirname(os.path.abspath(__file__))
STORY="story" in sys.argv[1:]  # python build_aviso_clases_suspendidas_muros.py story -> 1080x1920
W,H=(1080,1920) if STORY else (1080,1350)
S=200 if STORY else 0   # story: push content below the top safe zone
Y=(249,235,30); K=(14,14,14); R=(220,35,40)
fd=os.path.join(here,"fonts")
ANTON=lambda sz: ImageFont.truetype(os.path.join(fd,"anton-latin-400-normal.woff"),sz)
OSW=lambda sz,w=700: ImageFont.truetype(os.path.join(fd,f"oswald-latin-{w}-normal.woff"),sz)

img=Image.new("RGBA",(W,H),Y+(255,))
d=ImageDraw.Draw(img)
d.polygon([(0,0),(W,0),(W,300+S),(0,370+S)],fill=K)
logo=Image.open(os.path.join(here,"logo-muros.png")).convert("RGBA")
logo.thumbnail((380,215),Image.LANCZOS)
img.alpha_composite(logo,((W-logo.width)//2,50+(240 if STORY else 0)))
d=ImageDraw.Draw(img)

d.text((W//2,445+S),"AVISO IMPORTANTE",font=ANTON(96),fill=K,anchor="mm")
stamp=Image.new("RGBA",(900,160),(0,0,0,0)); sd=ImageDraw.Draw(stamp)
sd.rounded_rectangle((8,8,892,152),radius=20,outline=R,width=11)
sd.text((450,80),"CLASES SUSPENDIDAS",font=ANTON(96),fill=R,anchor="mm")
stamp=stamp.rotate(-3,expand=True,resample=Image.BICUBIC)
img.alpha_composite(stamp,((W-stamp.width)//2,505+S))
d=ImageDraw.Draw(img)
d.text((W//2,815+S),"VIERNES 27/11",font=ANTON(120),fill=K,anchor="mm")

def row(y,name,time):
    d.rectangle((90,y,W-90,y+110),fill=K)
    d.text((130,y+55),name,font=ANTON(70),fill="white",anchor="lm")
    d.text((W-130,y+55),time,font=ANTON(70),fill=Y,anchor="rm")
row(915+S,"FUNCIONAL","18 HS Y 19 HS")
row(1045+S,"ZUMBA","20 HS")

d.rectangle((0,1190+S,W,H),fill=K)
d.text((W//2,1238+S),"WHATSAPP 3489 588703",font=OSW(52),fill=Y,anchor="mm")
d.text((W//2,1300+S),"AV. MITRE 926 · CAMPANA",font=OSW(36,500),fill="white",anchor="mm")
img.convert("RGB").save(os.path.join(here,"aviso-clases-suspendidas-muros-historia.png" if STORY else "aviso-clases-suspendidas-muros.png"),quality=95)
