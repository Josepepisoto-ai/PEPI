"""Reel de venta: remera oficial Muros, promo lanzamiento $25.000.
python videos/remera-muros/build.py  -> videos/remera-muros/remera-muros-promo.mp4"""
import os, subprocess, math, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

here=os.path.dirname(os.path.abspath(__file__))
root=os.path.dirname(os.path.dirname(here))
UP="/root/.claude/uploads/4306f732-d120-550e-99c9-b9fa846f5f30"
IMG="/tmp/claude-0/-home-user-PEPI/4306f732-d120-550e-99c9-b9fa846f5f30/images"
V1=os.path.join(UP,"6ff5be50-WhatsApp_Video_2026-11-10_at_09.23.32.mp4")  # black tee
V2=os.path.join(UP,"0bab9dfc-WhatsApp_Video_2026-11-10_at_09.23.38.mp4")  # white tee
TMP=os.path.join(here,"_tmp"); os.makedirs(TMP,exist_ok=True)
W,H,FPS=1080,1920,30
Y=(249,235,30,255); K=(14,14,14,255); R=(220,35,40,255)
fd=os.path.join(root,"posts","fonts")
ANTON=lambda s: ImageFont.truetype(os.path.join(fd,"anton-latin-400-normal.woff"),s)
OSW=lambda s: ImageFont.truetype(os.path.join(fd,"oswald-latin-700-normal.woff"),s)
LOGO=Image.open(os.path.join(root,"posts","logo-muros.png")).convert("RGBA")

def boxed(d,cx,y,text,font,fg,bg,pad=(36,14)):
    w=d.textlength(text,font=font); a,b=font.getbbox(text)[1],font.getbbox(text)[3]
    d.rectangle((cx-w/2-pad[0],y,cx+w/2+pad[0],y+(b-a)+2*pad[1]),fill=bg)
    d.text((cx-w/2,y+pad[1]-a),text,font=font,fill=fg)
    return y+(b-a)+2*pad[1]

def credit(d,y=1545):
    # supplier credit, shown on every clip
    f=OSW(34); t="Remeras por @bolsalogo"; w=d.textlength(t,font=f)
    d.rounded_rectangle((W/2-w/2-26,y,W/2+w/2+26,y+58),radius=29,fill=(0,0,0,170))
    d.text((W/2,y+29),t,font=f,fill="white",anchor="mm")

def overlay(name,lines,logo=True,burst=None,credit_y=1545):
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    credit(d,credit_y)
    if logo:
        lg=LOGO.copy(); lg.thumbnail((230,130)); im.alpha_composite(lg,(W-lg.width-50,250))
    y=None
    for kind,text,size,yy in lines:
        y=yy if yy is not None else y+18
        f=ANTON(size)
        if kind=="y": y=boxed(d,W/2,y,text,f,K,Y)
        elif kind=="k": y=boxed(d,W/2,y,text,f,Y,K)
        elif kind=="w": y=boxed(d,W/2,y,text,f,K,(255,255,255,255))
    if burst:
        cx,cy,r=burst
        pts=[(cx+(r if i%2==0 else r*0.86)*math.cos(math.pi*i/20-math.pi/2),cy+(r if i%2==0 else r*0.86)*math.sin(math.pi*i/20-math.pi/2)) for i in range(40)]
        d.polygon(pts,fill=R)
        d.ellipse((cx-r*.8,cy-r*.8,cx+r*.8,cy+r*.8),outline=(255,255,255,255),width=5)
        d.text((cx,cy-70),"PRECIO",font=OSW(30),fill="white",anchor="mm")
        d.text((cx,cy-36),"LANZAMIENTO",font=OSW(30),fill="white",anchor="mm")
        d.text((cx,cy+32),"$25.000",font=ANTON(80),fill="white",anchor="mm")
    p=os.path.join(TMP,name+".png"); im.save(p); return p

# (source, start, dur, overlay); source is a video path or an image path
# text sits on the chest (between face and shirt logo) or below the logo, never on it
segs=[
 (V1,10.0,3.0,overlay("a",[("k","¡SÚPER PROMO",96,640),("k","LANZAMIENTO!",96,None),("y","REMERA OFICIAL MUROS",60,1330)])),
 (V1,13.0,2.6,overlay("b",[("y","EN NEGRA",110,1320)])),
 (V2,1.0,2.6,overlay("c",[("w","Y EN BLANCA",110,1320)])),
 (os.path.join(IMG,"2.jpg"),0,2.6,overlay("d",[("y","PARA ENTRENAR",90,1250),("k","CON LOS COLORES DE MUROS",56,None)])),
 (V2,11.0,3.0,overlay("e",[],burst=(850,820,175))),
 (V2,8.0,2.6,overlay("f",[("k","¡SOLO LAS PRIMERAS",80,650),("k","30 REMERAS!",110,None)])),
 (os.path.join(root,"posts","remera-muros-venta-historia.png"),0,4.2,overlay("g",[],logo=False,credit_y=1600)),
]

def run(cmd): subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
parts=[]
for i,(src,ss,dur,ov) in enumerate(segs):
    out=os.path.join(TMP,f"s{i}.mp4"); parts.append(out)
    fade=f"fade=t=in:st=0:d=0.15"
    if src.endswith(".mp4"):
        # selfie videos come mirrored: flip back so the logo reads correctly
        base=f"[0:v]trim=start={ss}:duration={dur},setpts=PTS-STARTPTS,hflip,scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps={FPS},eq=contrast=1.05:saturation=1.1"
        inp=["-i",src]
    else:
        n=int(dur*FPS); last=src.endswith("historia.png")
        zoom="1+0.03*on/%d"%n if last else "1.0+0.12*on/%d"%n
        base=f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},zoompan=z='{zoom}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={n}:s={W}x{H}:fps={FPS}"
        inp=["-loop","1","-t",str(dur),"-i",src]
    if ov:
        fc=f"{base}[b];[b][1:v]overlay=0:0,{fade},format=yuv420p[v]"; inp+=["-i",ov]
    else:
        fc=f"{base},{fade},format=yuv420p[v]"
    run(["ffmpeg","-y",*inp,"-filter_complex",fc,"-map","[v]","-t",str(dur),"-r",str(FPS),"-c:v","libx264","-crf","18","-preset","medium",out])

lst=os.path.join(TMP,"list.txt")
open(lst,"w").write("".join(f"file '{p}'\n" for p in parts))
silent=os.path.join(TMP,"video.mp4")
run(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,"-c","copy",silent])

# simple 120 bpm beat (kick, clap, hats, bass) so the reel isn't silent
total=sum(s[2] for s in segs); sr=44100; n=int(total*sr); t=np.arange(n)/sr; out=np.zeros(n)
beat=0.5
def env(tt,dec): return np.exp(-tt/dec)
for k in range(int(total/beat)+1):
    st=k*beat; i0=int(st*sr); m=min(n,i0+int(0.4*sr)); tt=t[i0:m]-st
    out[i0:m]+=0.9*np.sin(2*np.pi*(50+90*env(tt,0.03))*tt)*env(tt,0.12)          # kick
    if k%2==1:
        m2=min(n,i0+int(0.2*sr)); out[i0:m2]+=0.35*np.random.uniform(-1,1,m2-i0)*env(t[i0:m2]-st,0.05)  # clap
    h=int((st+beat/2)*sr); m3=min(n,h+int(0.05*sr))
    if h<n: out[h:m3]+=0.15*np.random.uniform(-1,1,m3-h)*env(t[h:m3]-st-beat/2,0.012)   # off-beat hat
bassnotes=[55,55,65.4,49]
for k in range(int(total/beat)+1):
    st=k*beat; i0=int(st*sr); m=min(n,i0+int(beat*sr)); tt=t[i0:m]-st
    f=bassnotes[(k//4)%4]; out[i0:m]+=0.3*np.sign(np.sin(2*np.pi*f*tt))*env(tt,0.25)
fadeo=int(1.5*sr); out[-fadeo:]*=np.linspace(1,0,fadeo)
out=out/np.abs(out).max()*0.8
wav=os.path.join(TMP,"beat.wav")
with wave.open(wav,"wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out*32767).astype(np.int16).tobytes())
final=os.path.join(here,"remera-muros-promo.mp4")
run(["ffmpeg","-y","-i",silent,"-i",wav,"-map","0:v","-map","1:a","-c:v","copy","-af","loudnorm=I=-14:TP=-1.5","-c:a","aac","-b:a","192k","-ar","44100","-shortest","-movflags","+faststart",final])
print(final,total)
