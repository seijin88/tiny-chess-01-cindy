import json
import os
import urllib.request
import random
URL=os.environ.get("MAKEFUN_ENV_URL")
N=(31,33,14,18,-31,-33,-14,-18)
G=(17,15,-17,-15)
S=(16,-16,1,-1)
Y=G+S
V=(0,100,320,335,500,950,0)
PH=(0,0,1,1,2,4,0)
I=30000
rng=random.Random(0)
ZH=[[rng.getrandbits(64)for _ in range(128)]for _ in range(13)]
ZS=rng.getrandbits(64)
ZC=[rng.getrandbits(64)for _ in range(16)]
ZE=[rng.getrandbits(64)for _ in range(129)]
PS={}
PE={}
for p in range(-6,7):
 if not p:continue
 w=1 if p>0 else -1;t=abs(p)
 for i in range(128):
  if i&136:continue
  f=i&7;r=i>>4;r=r if w==1 else 7-r
  c=min(f,7-f);center=c+min(r,7-r)
  if t==1:
   a=7*r+4*c-(10 if r==1 and f in(3,4)else 0)
   z=13*r+3*c
  elif t==2:a=12*center-48-(15 if r==0 else 0);z=8*center-32
  elif t==3:a=7*center-20;z=5*center-15
  elif t==4:a=3*c+20*(r==6);z=4*center
  elif t==5:a=3*center-10;z=5*center-15
  else:a=-8*center-12*r+30*(r==0 and f in(1,2,6));z=12*center-36
  PS[p,i]=w*(V[t]+a);PE[p,i]=w*(V[t]+z)
b=[0]*128
king=[0,0]
rights=0
ep=-1
mg=0
eg=0
phase=0
zh=0
# Transposition table, history heuristic, killer moves, node counter, limit
TT={}
H={}
kill=[[]for _ in range(100)]
nodes=0
LIMIT=60000
class Stop(Exception):
 pass

def put(i,p):
 global mg,eg,phase,zh
 old=b[i]
 if old:mg-=PS[old,i];eg-=PE[old,i];phase-=PH[abs(old)];zh^=ZH[old+6][i]
 b[i]=p
 if p:mg+=PS[p,i];eg+=PE[p,i];phase+=PH[abs(p)];zh^=ZH[p+6][i]

def load(fen):
 global rights,ep,mg,eg,phase,zh
 b[:]=[0]*128;mg=eg=phase=zh=0
 fields=fen.split()
 i=112
 for c in fields[0]:
  if c=="/":
   i-=24
  elif c.isdigit():i+=int(c)
  else:
   p=" pnbrqk".index(c.lower())*(1 if c.isupper()else -1)
   put(i,p)
   if abs(p)==6:king[p<0]=i
   i+=1
 rights=sum(v for c,v in zip("KQkq",(1,2,4,8))if c in fields[2])
 ep=-1 if fields[3]=="-"else ord(fields[3][0])-97+16*(int(fields[3][1])-1)
 return 1 if fields[1]=="w"else -1

def key(w):return zh^(ZS if w<0 else 0)^ZC[rights]^ZE[ep+1]

def attacked(s,w):
 for d in(-15*w,-17*w):
  j=s+d
  if not j&136 and b[j]==w:return True
 for d in N:
  j=s+d
  if not j&136 and b[j]==2*w:return True
 for d in Y:
  j=s+d
  if not j&136 and b[j]==6*w:return True
  while not j&136:
   p=b[j]
   if p:
    if p*w>0 and(abs(p)==5 or abs(p)==(3 if d in G else 4)):return True
    break
   j+=d
 return False

def generate(w,tactical=False):
 moves=[]
 for i in range(128):
  if i&136 or b[i]*w<=0:continue
  t=abs(b[i])
  if t==1:
   j=i+16*w
   if not j&136 and not b[j]:
    if j>>4 in(0,7):moves.extend(i|(j<<7)|(p<<14)for p in(5,2,4,3))
    elif not tactical:
     moves.append(i|(j<<7))
     if i>>4==(1 if w>0 else 6)and not b[j+16*w]:moves.append(i|((j+16*w)<<7))
   for d in(15*w,17*w):
    j=i+d
    if not j&136 and(b[j]*w<0 or j==ep):
     if j>>4 in(0,7):moves.extend(i|(j<<7)|(p<<14)for p in(5,2,4,3))
     else:moves.append(i|(j<<7))
  else:
   for d in N if t==2 else G if t==3 else S if t==4 else Y:
    j=i+d
    while not j&136:
     p=b[j]
     if p*w>0:break
     if p or not tactical:moves.append(i|(j<<7))
     if p or t in(2,6):break
     j+=d
   if t==6 and not tactical and i==(4 if w>0 else 116):
    shift=0 if w>0 else 2
    if rights&(1<<shift)and b[i+3]==4*w and not(b[i+1]or b[i+2])and not any(attacked(i+d,-w)for d in(0,1,2)):moves.append(i|((i+2)<<7))
    if rights&(2<<shift)and b[i-4]==4*w and not(b[i-1]or b[i-2]or b[i-3])and not any(attacked(i-d,-w)for d in(0,1,2)):moves.append(i|((i-2)<<7))
 return moves

def undo(u):
 global rights,ep,mg,eg,phase,zh
 changes,rights,ep,mg,eg,phase,zh,k0,k1=u
 for i,p in changes:b[i]=p
 king[:]=[k0,k1]

def make(m,w):
 global rights,ep
 i=m&127;j=(m>>7)&127;promotion=m>>14;p=b[i]
 changes=[(i,p),(j,b[j])]
 if abs(p)==1 and j==ep and not b[j]:changes.append((j-16*w,b[j-16*w]))
 if abs(p)==6 and abs(j-i)==2:
  x,y=(i+3,i+1)if j>i else(i-4,i-1)
  changes.extend(((x,b[x]),(y,b[y])))
 u=(changes,rights,ep,mg,eg,phase,zh,*king)
 put(i,0);put(j,promotion*w if promotion else p)
 if len(changes)==3:put(j-16*w,0)
 if len(changes)==4:put(x,0);put(y,4*w)
 ep=i+16*w if abs(p)==1 and abs(j-i)==32 else -1
 if abs(p)==6:
  king[w<0]=j;rights&=12 if w>0 else 3
 for sq in(i,j):rights&={0:13,7:14,112:7,119:11}.get(sq,15)
 if attacked(king[w<0],-w):undo(u);return None
 return u

# eval
def evaluate(w):
 ph=min(24,phase)
 return w*((mg*ph+eg*(24-ph))//24)+12

def order(m,w,tt,ply):
 if m==tt:return 10000000
 i=m&127;j=(m>>7)&127;t=abs(b[j]);p=abs(b[i]);promotion=m>>14
 if t or p==1 and j==ep:return 100000+16*V[t or 1]-V[p]+V[promotion]
 if promotion:return 100000+V[promotion]
 if m in kill[ply]:return 90000
 return H.get((w,m),0)

def tick():
 global nodes
 nodes+=1
 if nodes>LIMIT:raise Stop

def qsearch(w,a,beta,ply):
 tick();check=attacked(king[w<0],-w)
 if ply>=48:return evaluate(w)
 if not check:
  static=evaluate(w)
  if static>=beta:return static
  a=max(a,static)
 count=0
 for m in sorted(generate(w,not check),key=lambda m:order(m,w,0,ply),reverse=True):
  if not check and not m>>14 and static+V[abs(b[(m>>7)&127])or 1]+200<a:continue
  u=make(m,w)
  if u is None:continue
  count+=1
  try:score=-qsearch(-w,-beta,-a,ply+1)
  finally:undo(u)
  if score>=beta:return score
  a=max(a,score)
 return -I+ply if check and not count else a

# search
def search(w,a,beta,depth,ply,path,null=True):
 global ep
 pk=key(w)
 if pk in path:return 0
 if depth<=0:return qsearch(w,a,beta,ply)
 tick()
 if ply>=48:return evaluate(w)
 ic=attacked(king[w<0],-w)
 if ic:depth+=1
 oa=a
 ce=TT.get(pk)
 pref=ce[3]if ce else 0
 if ce and ce[0]>=depth and abs(ce[1])<I-100:
  cs=ce[1];bd=ce[2]
  if bd==0 or bd==1 and cs>=beta or bd==-1 and cs<=a:return cs
 st=evaluate(w)
 if not ic and beta-a==1 and depth<4 and abs(beta)<I-100 and st-100*depth>=beta:return st
 if null and depth>=3 and not ic and phase>2 and st>=beta and any(1<p*w<6 for p in b):
  oep=ep;ep=-1
  try:ns=-search(-w,-beta,1-beta,depth-3,ply+1,path,False)
  finally:ep=oep
  if ns>=beta:return ns
 best=-I;bm=0;count=0
 path.add(pk)
 try:
  for m in sorted(generate(w),key=lambda x:order(x,w,pref,ply),reverse=True):
   q=not b[(m>>7)&127]and not(m>>14)and not(abs(b[m&127])==1 and (m>>7)&127==ep)
   u=make(m,w)
   if u is None:continue
   gc=attacked(king[w>0],w)
   red=int(count>=3 and depth>=3 and q and not ic and not gc and m not in kill[ply])
   try:
    if not count:v=-search(-w,-beta,-a,depth-1,ply+1,path)
    else:
     v=-search(-w,-a-1,-a,depth-1-red,ply+1,path)
     if red and v>a:v=-search(-w,-a-1,-a,depth-1,ply+1,path)
     if a<v<beta:v=-search(-w,-beta,-a,depth-1,ply+1,path)
   finally:undo(u)
   count+=1
   if v>best:best=v;bm=m
   a=max(a,v)
   if a>=beta:
    if q:
     kill[ply][:]=[m]+kill[ply][:1]
     H[w,m]=min(80000,H.get((w,m),0)+depth*depth)
    break
 finally:path.remove(pk)
 if not count:return -I+ply if ic else 0
 if abs(best)<I-100:TT[pk]=(depth,best,1 if best>=beta else -1 if best<=oa else 0,bm)
 return best

_B='014e5a02ad102335a0296204ab840030406a88e011850941da02a4509f3d0029c30d829401810103d8103141158c110232516100e02b06190ae6011f31ce45e031f11de99f0383425dc140181026a8e60386226c519003042a4a01020b13346db00b8636c9230296237294b003043936a8033e23cf34d03b734111fb018c34215f90216343ba5d0120245ee7401083468663020b04af4f1031f4577f7000931580b67021d45bf531018e15d6cf1031d35e151e01a146d4579002056dc92001953711cf603171755d4a013b776108c029e378add703b747c08d5029b47c8321018107f1b2e0092380670602124837e840118585a3c5030e28676ae0387186e64f018918794bb012b6889a7803a718a3d80023668ad085039738ad60e01b728ae5c6012868bfb34038f48df136021d58e1de4018e48fa73703a7590a20c0110191de36031029d50d7009a5a2f8f3009b3a46c7002132a4de8b01155a5e11e033f6a63645009a5a6fdaf038f0a7b248021d4a863ee00923aaab6f018a1aca24e01a32ad54a901bc7ad8341010b0ae702601800b1343a01a42b189bc01a23b7c12b03172b9c90801922ba1bc802942bedcbb02234c0bb5703153c3a3c602870c46ded01092c494e4021b2c5e5d5031d5c5f6f0028e2c7ac3e020a2cb75b702060cbb43502132ce580402263cef6c3178e1cfc6e4028c1d15328022f2d189b302b66d401ee023e7d5a43b01397d7cc2e01113db25d1179e3df6e9901bc7e0e6f000105e18dff01286e1e01b012b6e3c27901922ea1ace01a95eb5ace03275ec170f038b1f18fdb01083f1b412020f1fbb33d030d1'
BOOK={int(_B[i:i+6],16):int(_B[i+6:i+11],16)for i in range(0,len(_B),11)}
def choose(w,history):
 global nodes,LIMIT
 bm=BOOK.get(key(w)&16777215)
 if bm in generate(w):
  saved=make(bm,w)
  if saved is not None:undo(saved);return bm
 TT.clear();H.clear()
 for k in kill:k.clear()
 nodes=0;LIMIT=100000 if phase<8 else 75000
 legal=[]
 for m in generate(w):
  saved=make(m,w)
  if saved is not None:undo(saved);legal.append(m)
 legal.sort()
 best=legal[0]
 scores={};root=key(w)
 for depth in range(1,13):
  a=-I;pick=best
  try:
   for m in sorted(legal,key=lambda x:(x!=best,-scores.get(x,-I),x)):
    saved=make(m,w)
    try:v=-search(-w,-I,-a,depth-1,1,history|{root})
    finally:undo(saved)
    scores[m]=v
    if v>a:a=v;pick=m
   best=pick
  except Stop:break
  if abs(a)>I-100:break
 return best

def uci(m):
 i=m&127;j=(m>>7)&127;p=m>>14
 return "abcdefgh"[i&7]+str(1+(i>>4))+"abcdefgh"[j&7]+str(1+(j>>4))+(" pnbrqk"[p]if p else "")

def post(path,data):
 return json.load(urllib.request.urlopen(urllib.request.Request(URL+path,json.dumps(data).encode())))

if __name__=="__main__":
 while True:
  g=post("/game",{})
  if g["status"]=="done":break
  history=set()
  while g["status"]=="your_move":
   w=load(g["fen"]);root=key(w);m=uci(choose(w,history))
   assert m in g["legal_moves"],m
   history.add(root)
   g=post("/move",{"game":g["game"],"move":m})