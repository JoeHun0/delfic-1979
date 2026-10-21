import numpy as np
exec(open('fit2.py').read().split('res=[]')[0])
chainsum=np.zeros(30)
for l in open('fort.78'):
    lc,ld,b,p,v=l.split(); chainsum[int(ld)-1]+=float(v)
soil=ours-chainsum
print("soil share %.3f%%"%(soil.sum()/ours.sum()*100), "soil/ours by class", np.round(soil/ours*100,3))
a=(soil[m]@D[m])/(soil[m]@soil[m]); r=D[m]-a*soil[m]
print("soil-shape fit: scale x%.2f resid %.4f"%(a,np.sqrt((r**2).sum()/(D[m]**2).sum())))
