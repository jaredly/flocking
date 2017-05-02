import pygame,random,math
from random import randrange as rr
from pygame.locals import *
import time
from math import pi,sin,cos,atan2,sqrt

pygame.init()


def rot_around((x,y),(a,b),r):
    d = dst(x-a,y-b)
    r+=math.atan2(x-a,y-b)-pi/2
    return int(a+math.cos(r)*d),int(b+math.sin(r)*d)

def rot_pts(ang,pts):
    ptn = []
    for [x,y] in pts:
        dr = atan2(x,y)
        dst = sqrt(x**2+y**2)
        dr+=ang
        ptn.append([cos(dr)*dst,sin(dr)*dst])
    return ptn

def arr_add(*arrs):
    ln = min([len(ar) for ar in arrs])
    return [sum([ar[i] for ar in arrs]) for i in range(ln)]

def stuff(fn,*a,**b):
    def meta(*c,**d):
        d.update(b)
        return fn(*(a+c),**d)
    return meta

def arrow(scr,color,(x,y),(a,b),w=1):
    sz = 5*w
    pygame.draw.line(scr,color,[x,y],[a,b],w)
    dr = -atan2(x-a,y-b)+pi
    dst = sqrt((a-x)**2+(b-y)**2)
    pts = rot_pts(dr,[[dst-sz,-sz/2.5],[dst,0],[dst-sz,sz/2.5]])
    pts = map(stuff(arr_add,[x,y]),pts)
    pygame.draw.polygon(scr,color,pts)

def dst(x,y):
    return sqrt(x**2+y**2)

class Vector:
    def __init__(self,t,m):
        self.t=t
        self.m=m
    @classmethod
    def from_pos(cls,x,y):
        t = atan2(y,x)
        m = dst(x,y)
        return Vector(t,m)
    def x(self):
        return self.part(0)##cos(self.t)*self.m
    def y(self):
        return self.part(pi/2)#sin(self.t)*self.m
    def pos(self):
        return self.x(),self.y()
    def __add__(self,other):
        x = self.x()+other.x()
        y = self.y()+other.y()
        return Vector.from_pos(x,y)
    def reflect(self,normal):
        self.t += 2*(normal-self.t)
    def part(self,angle):
        return cos(self.t-angle)*self.m

class Sprite:
    logging = False
    arrow = False
    wire = False
    def __init__(self,parent,pos,size,color=None):
        self.parent = parent
        self.pos = list(pos)
        self.size = size
        self.color = color or [rr(255) for x in [1,2,3]]
        self.v = Vector(0,0)
        self.looping = False
    
    ## main calculation funcs
    
    def step(self):
        pass ## override
    
    def event(self,e):
        pass ## override
    
    def draw(self,screen):
        x,y = self.pos
        x-=self.parent.pos[0]
        y-=self.parent.pos[1]
        if self.arrow:
            pts = [rot_around(a,[0,0],self.v.t+pi/2) for a in [[-self.size/2,-self.size],[0,self.size],[self.size/2,-self.size]]]
            pygame.draw.polygon(screen,self.color,[[a+x,b+y] for a,b in pts],self.wire)
        else:
            pygame.draw.circle(screen,self.color,[int(x),int(y)],self.size,self.wire)
        epos = x+self.v.x()*3,y+self.v.y()*3
        xpos = epos[0],y
        ypos = x,epos[1]
        if self.logging:arrow(screen,[255,255,255],[x,y],epos,1)
    
    def update(self):
        self.pos[0]+=self.v.x()
        self.pos[1]+=self.v.y()
        if self.looping:
            self.loop_pos(self.looping)
    
    ## now all these are just helper funcs
    
    def loop_pos(self,*ar):
        if not ar or ar==[True]:
            x=y=0
            a,b = self.parent.size
        elif len(ar)==4:
            x,y,a,b=ar
        else:raise Exception,"Wrong number of arguments"
        if self.pos[0]<x:
            self.pos[0]=a
        elif self.pos[0]>a:
            self.pos[0]=x
        if self.pos[1]<y:
            self.pos[1]=b
        elif self.pos[1]>b:
            self.pos[1]=y
    
    def limit_speed(self,much):
        if self.v.m>much:self.v.m=much
        if self.v.m<-much:self.v.m=-much
    
    def limit_pos(self,x=0,y=0,a=None,b=None,bounce=False):
        if a is None:
            a = self.parent.size[0]
        if b is None:
            b = self.parent.size[1]
        if self.pos[0]-self.size<x:
            self.pos[0]=x+self.size
            if bounce:self.bounce_against(pi/2)
        if self.pos[1]-self.size<y:
            self.pos[1]=y+self.size
            if bounce:self.bounce_against(pi)
        if self.pos[0]+self.size>=a:
            self.pos[0]=a-self.size
            if bounce:self.bounce_against(pi/2*3)
        if self.pos[1]+self.size>=b:
            self.pos[1]=b-self.size
            if bounce:self.bounce_against(0)
    
    def bounce(self,other):
        if not self.collides_with(other):return False
        dt = self.dir_to(other.pos)
        self.bounce_against(dt)
    
    def bounce_against(self,normal):
        self.v.reflect(normal)
    
    def dir_to(self,(x,y)):
        if not self.looping:
            return math.atan2(y-self.pos[1],x-self.pos[0])
        
    def push(self,v):
        self.v += v
    
    def move(self,x,y):
        self.pos[0]+=x
        self.pos[1]+=y
    
    def move_to(self,x,y):
        self.pos = [x,y]
        
    def push_dir(self,dir,speed):
        self.v+=Vector(dir,speed)
        
    def move_dir(self,dir,speed):
        self.pos[0]+= math.cos(dir)*speed
        self.pos[1]+= math.sin(dir)*speed
        
    def push_towards(self,pos,speed):
        dir = math.atan2(pos[1]-self.pos[1],pos[0]-self.pos[0])
        self.push_dir(dir,speed+(speed>0 and 1 or -1)*self.size/10.0)
        
    def move_towards(self,pos,speed):
        dir = math.atan2(pos[1]-self.pos[1],pos[0]-self.pos[0])
        self.move_dir(dir,speed)
        
    def dist_to(self,pos):
        return math.sqrt((pos[0]-self.pos[0])**2+(pos[1]-self.pos[1])**2)
    
    def collides_with(self,other):
        return self.dist_to(other.pos)<=self.size+other.size
    
    def collide_point(self,pos):
        return self.dist_to(pos)<=self.size


class Game:
    size = None
    grid = None
    fps = 40
    bg = [0,0,0]
    def __init__(self,**conf): ## size=None,bg=[0,0,0],fps=40,grid = False): ## grid=(bx,by,[bcolor])
        for attr in ("size","grid","fps","bg"):
            if getattr(self,attr) is not None:
                conf[attr] = getattr(self,attr)
            elif not conf.has_key(attr):
                conf[attr] = None
        self.screen = pygame.display.set_mode(conf["size"])
        self.objects = []
        self.running = False
        self.bg = conf["bg"] or [0,0,0]
        self.size = conf["size"]
        self.clock = pygame.time.Clock()
        self.pos = [0,0]
        self.grid = conf["grid"]
        self.fps = conf["fps"]
        self.debug = ""
        self.load()
        
    def load(self):
        pass
    
    def step(self):
        [o.step() for o in self.objects]
        [o.update() for o in self.objects]
        
    def draw(self):
        if self.grid:
            self.draw_grid(*self.grid)
        [o.draw(self.screen) for o in self.objects]
        t = pygame.font.Font(None,24).render(str(self.clock.get_fps()),1,[50,50,50])
        self.screen.blit(t,(0,0))
        t = pygame.font.Font(None,24).render(str(self.debug),1,[50,50,50])
        self.screen.blit(t,(0,30))
        
    def draw_grid(self,bx,by,color=[50,50,50]):
        ## every horiz
        for i in range(self.size[0]/bx+1):
            at = i*bx-self.pos[0]%bx
            pygame.draw.line(self.screen,color,(at,0),(at,self.size[1]))
        ## every vert
        for i in range(self.size[1]/by+1):
            at = i*by-self.pos[1]%by
            pygame.draw.line(self.screen,color,(0,at),(self.size[0],at))

    def events(self):
        for e in pygame.event.get():
            if e.type==QUIT:
                self.running = False
            self.event(e)
            [o.event(e) for o in self.objects]
    
    def follow(self,what,margin=50):
        if type(what) not in (list,tuple):
            what = what.pos
        x,y=self.pos
        if what[0]-x<margin:
            x -= margin - (what[0]-x)
        if what[0]-x>self.size[0]-margin:
            x -= self.size[0] - margin - (what[0]-x)
        if what[1]-y<margin:
            y -= margin - (what[1]-y)
        if what[1]-y>self.size[1]-margin:
            y -= self.size[1] - margin - (what[1]-y)
        self.pos = x,y
    
    def event(self,e):
        pass
        
    def loop(self):
        self.running = True
        while self.running:
            self.screen.fill(self.bg)
            self.step()
            self.events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.fps)
        pygame.display.quit()
