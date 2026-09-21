"""Measured mesh cross-sections, not a lighting/render preview."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
g=json.loads((R/'qa/softgoods09-mesh.json').read_text());q=json.loads((R/'qa/softgoods09-candidate-check.json').read_text())
c,r=g['parameters']['columns'],g['parameters']['rows'];n=c*r;v=g['vertices'];base=g['parameters']['bottom_z']
fig,axes=plt.subplots(2,1,figsize=(10,5.8),constrained_layout=True)
for ax,indices,axis,label in [(axes[0],[r//2*c+i for i in range(c)],0,'Width section'),(axes[1],[j*c+c//2 for j in range(r)],1,'Depth section')]:
 x=[v[i][axis]*100 for i in indices]
 top=[(v[i][2]-base)*100 for i in indices]
 bottom=[(v[n+i][2]-base)*100 for i in indices]
 ax.fill_between(x,bottom,top,color='#dfddd2',alpha=.75)
 ax.plot(x,top,color='#526269',lw=2,label='Puffed top')
 ax.plot(x,bottom,color='#a07647',lw=2,label='Compressed underside')
 for val in (q['original_local_bounds'][2][0],q['original_local_bounds'][2][1]):ax.axhline((val-base)*100,ls='--',color='#b4b9bd',lw=1)
 ax.axhline(0,color='#2a8468',lw=1.2,label='Actual bedcover contact height')
 ax.set(title=label,xlabel='Local distance (cm)',ylabel='Height above cover (cm)',ylim=(-3.2,14))
 ax.grid(alpha=.15);ax.set_aspect('equal',adjustable='box')
axes[0].legend(loc='lower center',ncol=3,fontsize=8)
fig.suptitle('Alcove pillow candidate / actual geometry sections\nDashed lines: original height envelope; no lighting or material change',fontsize=11)
fig.savefig(R/'qa/softgoods09-profile-check.png',dpi=150)
print('Saved measured profile QA.')
