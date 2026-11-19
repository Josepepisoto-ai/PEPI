from PIL import Image, ImageDraw, ImageFont
import os, sys
here=os.path.dirname(os.path.abspath(__file__))
STORY="story" in sys.argv[1:]  # python build_aviso_feriado_23_11_muros.py story -> 1080x1920
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

d.text((W//2,445+S),"FERIADO NACIONAL",font=ANTON(118),fill=K,anchor="mm")
d.text((W//2,640+S),"LUNES 23/11",font=ANTON(210),fill=K,anchor="mm")

stamp=Image.new("RGBA",(760,230),(0,0,0,0)); sd=ImageDraw.Draw(stamp)
sd.rounded_rectangle((8,8,752,222),radius=24,outline=R,width=14)
sd.text((380,115),"CERRADO",font=ANTON(170),fill=R,anchor="mm")
stamp=stamp.rotate(-6,expand=True,resample=Image.BICUBIC)
img.alpha_composite(stamp,((W-stamp.width)//2,765+S))
d=ImageDraw.Draw(img)
d.text((W//2,1130+S),"EL GIMNASIO PERMANECERÁ CERRADO",font=OSW(46),fill=K,anchor="mm")

d.rectangle((0,1190+S,W,H),fill=K)
d.text((W//2,1238+S),"WHATSAPP 3489 588703",font=OSW(52),fill=Y,anchor="mm")
d.text((W//2,1300+S),"AV. MITRE 926 · CAMPANA",font=OSW(36,500),fill="white",anchor="mm")
img.convert("RGB").save(os.path.join(here,"aviso-feriado-23-11-muros-historia.png" if STORY else "aviso-feriado-23-11-muros.png"),quality=95)
