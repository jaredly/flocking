import pygame,random,math
from random import randrange as rr
from pygame.locals import *
from sprite import Sprite,Game

## boids move in formation toward the cursor

from math import *
def rot_around((x,y),(a,b),r):
    d = dst((x,y),(a,b))
    r+=atan2(x-a,y-b)-pi/2
    return int(a+cos(r)*d),int(b+sin(r)*d)

def dst((x,y),(a,b)):
    return sqrt((x-a)**2+(y-b)**2)

class Guy(Sprite):
    def step(self):
        
        far = 50
        close = 40
        tooclose = 30
        
        closest = None
        
        for l in self.maps:
            for o in l:
                if o is self or isinstance(o,Rover):continue
                if not closest or self.dist_to(o.pos)<closest[0] and self.dist_to(o.pos)>=close:
                    closest = [self.dist_to(o.pos),o]
                ## collision avoidance
                if self.dist_to(o.pos)<tooclose:
                    self.push_towards(o.pos,-.2)
        if closest and closest[0]>=far:
            self.push_towards(closest[1].pos,.2)
        else:
            self.push_towards(self.parent.goal,.2)
        self.limit_speed(6)
    def draw(self,screen):
        self.limit_pos()
        pts = [rot_around(x,[0,0],self.v.t+pi/2) for x in [[-5,-10],[0,10],[5,-10]]]
        pygame.draw.lines(screen,self.color,1,[[x[0]+self.pos[0],x[1]+self.pos[1]] for x in pts])
        

size = [600,600]

class Rover(Sprite):
    def __init__(self,*a,**b):
        Sprite.__init__(self,*a,**b)
        self.goal = [rr(size[0]),rr(size[1])]
        #self.counter = 100
    def step(self):
        self.limit_pos()
        self.push_towards(self.goal,.1)
        self.limit_speed(7)
        if self.dist_to(self.goal)<50:
            self.goal = [rr(size[0]),rr(size[1])]
        self.parent.goal = self.pos


class Flock(Game):
    def __init__(self):
        Game.__init__(self,size=size,grid = [20,20],fps=45)
        self.goal = [size[0]/2,size[1]/2]
        self.load()
        self.map = []
        self.mpos = self.goal
        
    def load(self):
        self.objects = []#Rover(self,[rr(size[0]),rr(size[1])],15)]
        self.pos = [0,0]
        for i in range(40):
            self.objects.append(Guy(self,[rr(size[0]),rr(size[1])],5))
    
    def load_map(self):
        del self.map
        self.map = [[[] for x in range(self.size[0]/50)] for y in range(self.size[1]/50)]
        for b in self.objects:
            x = int(b.pos[0]/50)
            y = int(b.pos[1]/50)
            self.map[x][y].append(b)
            maps = [self.map[x][y]]
            if x>0:
                maps.append(self.map[x-1][y])
                if y>0:
                    maps.append(self.map[x-1][y-1])
                if y<self.size[1]/50-1:
                    maps.append(self.map[x-1][y+1])
            if y>0:
                maps.append(self.map[x][y-1])
            if x<self.size[0]/50-1:
                maps.append(self.map[x+1][y])
                if y<self.size[1]/50-1:
                    maps.append(self.map[x+1][y+1])
                if y>0:
                    maps.append(self.map[x+1][y-1])
            if y<self.size[1]/50-1:
                maps.append(self.map[x][y+1])
            try:del b.maps
            except:pass
            b.maps = maps
    
    def event(self,e):
        if e.type==MOUSEMOTION:
            self.mpos = e.pos
            self.goal = e.pos
    
    def step(self):
        self.load_map()
        if len(self.objects)<=1:
            self.load()
        Game.step(self)
Flock().loop()
