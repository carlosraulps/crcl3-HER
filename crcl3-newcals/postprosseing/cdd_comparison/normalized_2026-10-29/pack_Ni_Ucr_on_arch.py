from pathlib import Path
import numpy as np,hashlib
p=Path('/home/cr/simulations/crcl3-HER/crcl3-newcals/postprosseing/cdd_rigorous_output/CHGCAR_diff_Ni_Ucr')
text=p.read_text();lines=text.splitlines(keepends=True);n=sum(map(int,lines[6].split()));idx=8+n
while not lines[idx].strip():idx+=1
shape=list(map(int,lines[idx].split()));header=''.join(lines[:idx+1]);raw=np.fromstring(text[len(header):],sep=' ');assert raw.size==np.prod(shape)
vol=2532.773504755897
step=1e-8
q=np.rint(raw/vol/step).astype(np.int32)
assert abs(raw/vol-q.astype(float)*step).max()<=step/2+1e-12
out=Path('/tmp/fig4_ni_ucr_render_grid.npz')
np.savez_compressed(out,q=q,header=header,step=step,volume=vol,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
print(out,out.stat().st_size,'maximum_density_rounding_error',abs(raw/vol-q.astype(float)*step).max())
