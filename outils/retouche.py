import json,math,sys
S=sys.argv[1]
d=json.load(open(S+"/clustered.json"))
L=(47.0367,4.8432)
def km(a,b,c,e):
    p=math.pi/180; x=math.sin((c-a)*p/2)**2+math.cos(a*p)*math.cos(c*p)*math.sin((e-b)*p/2)**2
    return 12742*math.asin(math.sqrt(x))
def sh(t): return t  # les heures Immich sont déjà locales (malgré le Z)
for day in d['days']:
    for k in ('stops_major','stops_minor'):
        for s in day[k]:
            s['timeRange']="-".join(sh(x) for x in s['timeRange'].split('-')); s['photos']=[[i,sh(t)] for i,t in s['photos']]
    day['night']['photos']=[[i,sh(t)] for i,t in day['night']['photos']]
days=d['days']
for i,day in enumerate(days):
    rs=day['raw_segments']; n=day['night']; last=(i==len(days)-1)
    if rs and km(*rs[0]['points'][0],*L)>0.3: rs.insert(0,{"type":"road","points":[list(L),rs[0]['points'][0]]})
    # départ en footing depuis le logement, puis voiture depuis le logement
    if len(rs)>1 and rs[0]['type']=='foot' and rs[1]['type']=='road' and km(*rs[0]['points'][0],*L)<0.3 and km(*rs[1]['points'][0],*L)>0.3:
        import os
        if os.path.exists(S+"/footing.json"):  # tracé de la course relevé sur la capture de l'utilisateur (boucle depuis/vers le logement)
            rs[0]['points']=json.load(open(S+"/footing.json")); rs[1]['points'][0]=list(L)
        else:
            end=rs[0]['points'][-1]; rs[1]['points'][0]=list(L); rs.insert(1,{"type":"foot","points":[end,list(L)]})
    ph=n['photos']
    if ph and ph[0][1]<"18:00":   # groupe de journée, pas une soirée : devient un arrêt
        day['stops_major' if len(ph)>=6 else 'stops_minor'].append({"lat":n['lat'],"lon":n['lon'],"nPhotos":len(ph),"timeRange":ph[0][1]+"-"+ph[-1][1],"durationMin":0.0,"city":n['city'],"photos":ph}); n['photos']=[]
        endpt=[n['lat'],n['lon']]
    else: endpt=rs[-1]['points'][-1] if rs else list(L)
    if not last and km(*endpt,*L)>0.3 and rs: rs.append({"type":"road","points":[endpt,list(L)]})
    n.update(lat=L[0],lon=L[1])
json.dump(d,open(S+"/clustered2.json","w"),ensure_ascii=False)
print([(x['date'],len(x['stops_major']),len(x['stops_minor']),len(x['night']['photos'])) for x in days])
