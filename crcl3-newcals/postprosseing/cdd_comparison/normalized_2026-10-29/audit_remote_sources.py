from pathlib import Path
import json, hashlib, numpy as np
root=Path('/home/cr/simulations/crcl3-HER')
archive=root/'cdd_archive_cpx'; slabs=root/'cdd_frozen_slabs'; out=root/'crcl3-newcals/postprosseing/cdd_rigorous_output'
def read(p, grid=False):
 with p.open() as f:
  f.readline();s=float(f.readline());cell=np.array([[float(x) for x in f.readline().split()] for _ in range(3)])*s
  sym=f.readline().split();counts=list(map(int,f.readline().split()));mode=f.readline()
  if mode.lower().startswith('s'): mode=f.readline()
  xyz=np.array([[float(x) for x in f.readline().split()[:3]] for _ in range(sum(counts))])
  if mode.lower().startswith(('c','k')):xyz=xyz@np.linalg.inv(cell)
  if grid:
   line=f.readline()
   while not line.strip():line=f.readline()
   dims=tuple(map(int,line.split()));offset=f.tell()
   vals=np.fromstring(p.read_text()[offset:],sep=' ',count=int(np.prod(dims)))
   assert vals.size==np.prod(dims)
   return cell,xyz,dims,vals
  return cell,xyz
rows=[]
for m in ['Fe','Ni']:
 for u in ['Ucr','Uall']:
  tag=f'{m}_{u}'; c=archive/f'CHGCAR_cpx_{tag}'; s=slabs/f'{m}_slab_{u}'/'CHGCAR';i=archive/f'CHGCAR_iso_{tag}'
  cc,cx,cg,cv=read(c,True);sc,sx,sg,sv=read(s,True);ic,ix,ig,iv=read(i,True)
  dc,dx,dg,dv=read(out/f'CHGCAR_diff_{tag}',True)
  ds=cx[:-1]-sx;ds-=np.rint(ds);di=cx[-1:]-ix;di-=np.rint(di)
  txt=(s.parent/'OUTCAR').read_text(errors='replace'); vol=abs(np.linalg.det(cc))
  raw_delta=cv-sv-iv
  row=dict(tag=tag,source_cpx=str(c),source_slab=str(s),source_iso=str(i),grid=list(cg),cell_match=bool(np.allclose(cc,sc) and np.allclose(cc,ic)),grid_match=(cg==sg==ig==dg),slab_coordinate_error_A=float(np.linalg.norm(ds@cc,axis=1).max()),iso_coordinate_error_A=float(np.linalg.norm(di@cc,axis=1).max()),subtraction_max_error=float(abs(raw_delta-dv).max()),net_e=float(dv.mean()),cpx_e=float(cv.mean()),slab_e=float(sv.mean()),iso_e=float(iv.mean()),p99_e_A3=float(np.quantile(abs(dv),.99)/vol),positive_volume_A3=float(np.count_nonzero(dv/vol>=.005)*vol/dv.size),negative_volume_A3=float(np.count_nonzero(dv/vol<=-.005)*vol/dv.size),finished=('General timing and accounting' in txt),electronic_converged=('aborting loop because EDIFF is reached' in txt),sha256=hashlib.sha256((out/f'CHGCAR_diff_{tag}').read_bytes()).hexdigest())
  # Relevant VASP settings from the actual OUTCAR, not just the current INCAR.
  keys=['ENCUT','ISPIN','ISMEAR','SIGMA','LDAUU','LDAUL','LDAUTYPE','LEXCH','NKPTS','NELECT','EDIFF','LASPH','LMAXMIX']
  row['slab_settings']=[l.strip() for l in txt.splitlines() if any(k in l for k in keys)][:35]
  rows.append(row)
print(json.dumps(rows,indent=2))
