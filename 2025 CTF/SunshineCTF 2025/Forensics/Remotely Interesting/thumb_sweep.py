import os, subprocess
src = "dwm.exe.dmp"
outdir = "raw_candidates"; os.makedirs(outdir, exist_ok=True)

sizes = [(1366,768),(1024,768),(1920,1080)]
step = 16 * 1024 * 1024
L = os.path.getsize(src)
idx = 0

def try_slice(offset,w,h,fmt,idx):
    size = w*h*4
    with open(src,"rb") as f: f.seek(offset); buf=f.read(size)
    if len(buf)!=size: return
    raw=f"{outdir}/slice_{idx:05d}_{w}x{h}_{fmt}_off{offset}.raw"
    png=raw.replace(".raw",".png"); open(raw,"wb").write(buf)
    try:
        subprocess.run(["convert","-size",f"{w}x{h}","-depth","8",f"{fmt}:{raw}",png],check=True)
    except: pass
    finally: os.remove(raw)

for off in range(0,L,step):
  for (w,h) in sizes:
    for fmt in ("rgba","bgra"):
      try_slice(off,w,h,fmt,idx); idx+=1