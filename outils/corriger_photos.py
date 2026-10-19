# Photos prises en sous-sol (GPS faux) pendant la visite du Domaine Dubois (sam. 17, 14h02-15h24) : replacées sur le domaine
import json,math,sys
S=sys.argv[1]; p=json.load(open(S+"/photos.json")); D=(47.11263,4.93971); n=0
def km(a,b,c,e):
    q=math.pi/180; x=math.sin((c-a)*q/2)**2+math.cos(a*q)*math.cos(c*q)*math.sin((e-b)*q/2)**2; return 12742*math.asin(math.sqrt(x))
for x in p:
    if x['dt'].startswith('2026-10-17T') and '14:02'<=x['dt'][11:16]<='15:24' and km(x['lat'],x['lon'],*D)>0.3:
        x['lat'],x['lon']=D; n+=1
json.dump(p,open(S+"/photos.json","w"),ensure_ascii=False); print(n,"photos replacées")
