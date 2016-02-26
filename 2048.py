import pygame
import operator
import pygame.locals
import copy

from pygame.locals import *
from pygame import event

pygame.init()
fpsClock = pygame.time.Clock()
_SIZE = 4
_BLOCK_SIZE=100
_STARTY=_BLOCK_SIZE
_MAX=_SIZE*_BLOCK_SIZE
_RIM= 5
_2048=None
_GameEnd=None
_GameOver=None
windowSurfaceObj = pygame.display.set_mode((_MAX,_MAX+_STARTY))
pygame.display.set_caption('blocks')

redColor = pygame.Color(255,0,0)
greenColor = pygame.Color(0,255,0)
blueColor = pygame.Color(0,0,255)
whiteColor = pygame.Color (255,255,255)
lightblue = pygame.Color(173, 216, 230)
lighterblue = pygame.Color(235,255,255)
grey =  pygame.Color(145,141,142)
gold =  pygame.Color(255,215,0)
black=  pygame.Color(0,0,0)
granite = pygame.Color(131,126,124)
box1 =  pygame.Color(201,196,194)
color2 =(229,228,227)
color4 = pygame.Color(229,182,147)

colors = {2:(229,228,227),4:(229,228-20,227-40),8:(229,228-30,227-60),16:(229,150,100),
          32:(200,100,50),64:(150,60,30),128:(255,219,90),
          256:(229,200,70),512:(229,180,50),1024:(229,170,40),2048:(229,160,20),
          4096:(0,0,0),8192:(0,0,100),16384:(30,0,0),32768:(60,0,0)}
# Dictionaries have a function, get, which takes two parameters - the key you want,
# and a default value if it doesn't exist. eg:  colors.get(0,colors[4096]))
mousex,mousey = 0,0

fontObj  = pygame.font.Font('verdana.ttf',32)
fontObj2  = pygame.font.Font('verdana.ttf',32)
fontObj16  = pygame.font.Font('verdana.ttf',28)
fontObj128  = pygame.font.Font('verdana.ttf',26,bold=True)
fontObj1024  = pygame.font.Font('verdana.ttf',24,bold=True)
fontObj16384  = pygame.font.Font('verdana.ttf',23,bold=True)
fontObjSmall  = pygame.font.Font('verdana.ttf',22,bold=True)
fontObjbox1  = pygame.font.Font('verdana.ttf',18,bold=True)
fontObjbox2  = pygame.font.Font('verdana.ttf',12,bold=True)

fonts ={2:fontObj2,4:fontObj2,8:fontObj2,16:fontObj16,32:fontObj16,64:fontObj16,128:fontObj128,
        1024:fontObj1024,2048:fontObj1024,4096:fontObj1024,8192:fontObj1024,16384:fontObj16384,0:fontObjSmall}
#3 ways of creating dictionary. 1. assign one-by-one. 2. from tuples. 3 from parallel lists (straight forward)
fontBox={}
for num in range(1,16):
    fontBox[pow(2,num)]=fonts.get(pow(2,num),fonts[0]).render(str(pow(2,num)),True,granite if pow(2,num)<16 else whiteColor)

fontBox[0]=fonts[0].render(str(pow(2,num)),True,whiteColor)
fontBox[-1]=fontObjbox1.render('New Game',True,whiteColor)
fontBox[-2]=fontObjbox2.render('Best',True,whiteColor)
fontBox[-3]=fontObjbox2.render('Score',True,whiteColor)

fontBox[1]=fonts[0].render(str(pow(2,num)),True,grey)

startbox=_MAX-int(1.5*_BLOCK_SIZE)+_RIM
width = int(1.5*_BLOCK_SIZE)
newGameBox=pygame.Rect((startbox,_RIM,width-2*_RIM,_BLOCK_SIZE//2-2*_RIM))
bestBox=pygame.Rect((startbox,_BLOCK_SIZE//2+_RIM,width//2-2*_RIM,_BLOCK_SIZE//2-2*_RIM))
scoreBox=bestBox.move(_BLOCK_SIZE//2+5*_RIM,0)

newG_msg="New Game"
newG_msgSurfaceObj = fontBox[-1]
newG_msgRectobj = newG_msgSurfaceObj.get_rect()
newG_msgRectobj.center = newGameBox.center

best_msg="Best"
best_msgSurfaceObj = fontBox[-2]
best_msgRectobj = best_msgSurfaceObj.get_rect()
best_msgRectobj.center  = bestBox.move(16,6).topleft

score_msg="Score"
score_msgSurfaceObj = fontBox[-3]
score_msgRectobj = score_msgSurfaceObj.get_rect()
score_msgRectobj.center = scoreBox.move(20,6).topleft

# This program is a big mistake. Need to use objects
def makeRect(x,y,side):
    newRect= Rect(0,0,side,side)
    newRect.centerx = x*_BLOCK_SIZE +_BLOCK_SIZE//2
    newRect.centery =_STARTY+y*_BLOCK_SIZE +_BLOCK_SIZE//2
    return newRect

BoxSet=[]
for y in range(0,_SIZE):
    for x in range(0,_SIZE):
        BoxSet.append(makeRect(x,y,_BLOCK_SIZE-_RIM))

#soundObj = pygame.mixer.Sound('bounce.wav')

def checkPairable(myList):

    Matrix = [[0 for x in range(_SIZE)] for x in range(_SIZE)]
    for x,y,z in myList:
        Matrix[y][x]=z
    for j in range(0,_SIZE):
        for i in range(0,_SIZE-1):
            if Matrix [i][j]==Matrix[i+1][j] or Matrix [j][i]==Matrix[j][i+1]:
                return False #(pairable, no deadlock)
    return True #no pair,

def processMovementByMatrix(myList:list,directive:int):

    newList=[]
    Matrix = [[[0,x+y*_SIZE] for x in range(_SIZE)] for y in range(_SIZE)]
    for x,y,z in myList:
        Matrix[y][x][0]=z
#    Here it would had been much easier if i used stack style lists
    if directive == pygame.K_DOWN:  # 90 rotation
        Matrix=[list(elem) for elem in zip(*Matrix[::-1])]
        Matrix,animateList,score=addMatrix(Matrix)
        Matrix=[list(elem[::-1]) for elem in zip(*Matrix[::-1])][::-1]
    elif directive == pygame.K_UP:
        Matrix=[list(elem) for elem in zip(*Matrix)]
        Matrix,animateList,score=addMatrix(Matrix)
        Matrix=[list(elem) for elem in zip(*Matrix)]

    elif directive == pygame.K_LEFT:  # no rotation
        print('move left, no rotation\n')
        Matrix,animateList,score=addMatrix(Matrix)
    elif directive == pygame.K_RIGHT:  # 180 rotation
        print('move right, rotate 180\n')
        Matrix=[each [::-1] for each in Matrix[::-1]]
        Matrix,animateList,score=addMatrix(Matrix)
        Matrix=[each [::-1] for each in Matrix[::-1]]

    for j,line in enumerate(Matrix):
        for i,each in enumerate(line):
            if each!=0:
                newList.append([i,j,each])

    standStill = True if sorted(myList)==sorted(newList) else False

    return newList,(directive,animateList),standStill,score

def addMatrix(myList:list):

    global _2048
    newList=[]
    newLine=[]
    animateList=[]
    score=0
    lastPaired=False

    for line in myList:
        for counter,[each,i] in enumerate(line):
            if each ==0:
                pass
            elif len(newLine)>0 and newLine[-1]==each and not lastPaired:

                if counter < len(newLine) :
                    raise ValueError('height from gravity not higher than blocks underneath')
                animateList[-1][4]=False
                animateList.append([i,each,counter-len(newLine),False,True])  # Bool-1:Solid/disappear, Bool-2 = same/double
                newLine[-1]= 2*each
                score=score+2*each
                lastPaired=True
                if each==16:
                    print('16 reach,2048',_2048)
                if  each==1024 and '_2048' in globals() and _2048==None :

                    if not gameEND(True):
                        _2048=False
            else:
                animateList.append([i,each,counter-len(newLine),True,True])
                newLine.append(int(each))
                lastPaired=False

        lastPaired=False

        newLine.extend( [0] *(_SIZE-len(newLine)))
        newList.append(newLine)
        newLine=[]

    return newList,animateList,score

def getRandBox(myList):
    existing=[]
    for [x,y,z] in myList:
        existing.append(y*4+x)
    simpleEmpty=[x for x in range(0,16) if x not in existing]
    import random
    x=random.choice(simpleEmpty)
    z = random.randint(0,10)
    z = 2 if z <= 9 else 4
    return  [x%4,x//4,z]

def drawBG(myBoxList=None,Score=None):
    windowSurfaceObj.fill(lightblue)

    newRect=pygame.draw.rect(windowSurfaceObj,colors[16384],newGameBox,2)
    bestRect=pygame.draw.rect(windowSurfaceObj,colors[16384],bestBox,2)
    scoreRect=pygame.draw.rect(windowSurfaceObj,colors[16384],scoreBox,2)

    windowSurfaceObj.fill(granite,newRect)
    windowSurfaceObj.fill(colors[4],bestRect)
    windowSurfaceObj.fill(colors[4],scoreRect)

    for coord in BoxSet:
        myRect=pygame.draw.rect(windowSurfaceObj,whiteColor,coord,0)
        windowSurfaceObj.fill(lighterblue,myRect)


    windowSurfaceObj.blit(newG_msgSurfaceObj,newG_msgRectobj)
    windowSurfaceObj.blit(best_msgSurfaceObj,best_msgRectobj)
    windowSurfaceObj.blit(score_msgSurfaceObj,score_msgRectobj)
    if myBoxList!=None:
        for i in myBoxList[:-1]:
            drawBox(box=i)

        drawBox(box=myBoxList[-1],border=gold)
    updateScore(0 if Score==None else Score)

# Take score (int) and update it on window surface. Uses fontbox objects
def updateScore(score):
    msg=str(score)
    scoreCounterBoxObj = fontObjbox2.render(msg,True,grey)
    scoreCounterRectobj = scoreCounterBoxObj.get_rect()
    scoreCounterRectobj.center = scoreBox.move(0,10).center

    bestCounterBoxObj = fontObjbox2.render(msg,True,grey)
    bestCounterRectobj = bestCounterBoxObj.get_rect()
    bestCounterRectobj.center = bestBox.move(0,10).center
    windowSurfaceObj.blit(scoreCounterBoxObj,scoreCounterRectobj)
    windowSurfaceObj.blit(bestCounterBoxObj,bestCounterRectobj)



def drawBox(box=None,border=None,Rect=None):
    x,y,z=box
    fillColor=colors[z if z<32768 else -1 ]
    Rect = makeRect(x,y,_BLOCK_SIZE-_RIM) if Rect == None else Rect
    myRect=pygame.draw.rect(windowSurfaceObj,fillColor if border == None else border, Rect)
    msgRectObj = fontBox[z].get_rect()
    msgRectObj.center = myRect.center
    if border !=None:
        pass
        windowSurfaceObj.fill(fillColor, myRect.inflate(-5, -5))
    windowSurfaceObj.blit(fontBox[z],msgRectObj)

def drawRect(boxRect,value):
    myRect=pygame.draw.rect(windowSurfaceObj,colors[value if value<32768 else -1 ], boxRect)
    msgRectObj = fontBox[value].get_rect()
    msgRectObj.center = myRect.center
    windowSurfaceObj.blit(fontBox[value],msgRectObj)

def boxShift(boxRect,directive,shift):
    Shifter={pygame.K_DOWN:(0,+_BLOCK_SIZE//shift),pygame.K_UP:(0,-_BLOCK_SIZE//shift),
             pygame.K_LEFT:(-_BLOCK_SIZE//shift,0),pygame.K_RIGHT:(+_BLOCK_SIZE//shift,0)}
    return tuple(map(operator.add,boxRect, Shifter[directive]))

def boxMove(x1,y1,directive,move):
    if directive in (pygame.K_DOWN, pygame.K_UP):
        y1+= move if directive == pygame.K_DOWN else -move
    elif directive in (pygame.K_LEFT, pygame.K_RIGHT):
        x1+= move if directive == pygame.K_RIGHT else -move
    if x1 >=_SIZE or x1<0 or y1>= _SIZE or y1<0 : raise ValueError('block beyond boundaries')
    return x1,y1  # trivia: return type is tuple here

def animateNew(new,animatePlan,preList,score):
    x,y,z=new
    directive,animateList=animatePlan
    flickPerBlock=4  #4 ticks per block

    animateCounter=_SIZE*flickPerBlock
    step =  _BLOCK_SIZE//animateCounter #for new blocks and double blocks

    drawList=[[] for x in range(0,animateCounter)]

    if(len(animateList)!=len(preList)):
        raise ValueError("animateList!=preList: animate block instructions and pre-existing blocks must be same")

    for i,[ pos,value,move,willStaySolid,willNumFixed] in enumerate(animateList):
        x1,y1=pos%_SIZE,pos//_SIZE  # for all blocks except new

        if not preList.__contains__([x1,y1,value]): raise ValueError('animate block not found in prelist')
        if move >_SIZE : raise ValueError('cannot move beyond blocks boundaries')
        tempRect= makeRect(x1,y1,_BLOCK_SIZE-_RIM)

        drawList[0].append([value,tempRect])
        if willStaySolid and willNumFixed and move == 0:
            for frame in range(1,animateCounter):
                drawList[frame].append([value,tempRect])
        elif willStaySolid and willNumFixed:
            for frame in range(1,move*flickPerBlock):
                drawList[frame].append([value,copy.deepcopy(drawList[frame-1][-1][1])])
                #take the last frame's last rectangle position and shift it by flickPerBox
                drawList[frame][-1][1].center = boxShift(drawList[frame-1][-1][1].center, directive,flickPerBlock)

            x1,y1 = boxMove(x1,y1,directive,move)
            tempRect=makeRect(x1,y1,_BLOCK_SIZE-_RIM)
            for frame in range(move*flickPerBlock,animateCounter):
                drawList[frame].append([value,tempRect])

        elif not willStaySolid and not willNumFixed:
            raise ValueError('cant have both: vanishing and doubling')
        elif not willStaySolid:
            for frame in range(1,move*flickPerBlock):
                drawList[frame].append([value,copy.deepcopy(drawList[frame-1][-1][1])])
                drawList[frame][-1][1].center =  boxShift(drawList[frame-1][-1][1].center, directive,flickPerBlock)
        elif not willNumFixed:
            for frame in range(1,move*flickPerBlock):
                drawList[frame].append([value,copy.deepcopy(drawList[frame-1][-1][1])])
                drawList[frame][-1][1].center =  boxShift(drawList[frame-1][-1][1].center, directive,flickPerBlock)
            x1,y1 = boxMove(x1,y1,directive,move)
            growing = _BLOCK_SIZE//2  #starting size for double block
            for frame in range(animateCounter//2,animateCounter):   # generate frames for double block with zoom fx
                tempRect=makeRect(x1,y1,growing)
                growing = growing+step
                drawList[frame].append([value,tempRect])

    growing2 = _BLOCK_SIZE//2  # starting size for the one new block
    for frame in range(animateCounter//2,animateCounter):  #generate frames for the one new block with zoom fx
        tempRect=makeRect(x,y,growing2)
        growing2 = growing2+step
        drawList[frame].append([z,tempRect])
    #Begins animation
    for k,frame in enumerate(drawList) :
        drawBG(Score=score)
        for num,myRect in frame:
            drawRect(myRect,num)
        pygame.display.update()
        fpsClock.tick(60)

def gameEND(reached=False):
    animateCounter=25
    posx,posy = 0,0
    closing = pygame.Surface((_MAX,_MAX+_STARTY))  # the size of your rect

    End_msg="Game Over!" if not reached else "You Won!"
    End_msgSurfaceObj = fontObj.render(End_msg,True,granite)
    End_msgRectobj = End_msgSurfaceObj.get_rect()
    End_msgRectobj.center = (_BLOCK_SIZE*2,_BLOCK_SIZE*2)

    Try_msg= "Try Again?"  if not reached else "Continue!"
    Try_msgSurfaceObj = fontObjbox1.render(Try_msg,True,whiteColor)
    Try_msgRectobj = Try_msgSurfaceObj.get_rect()
    Try_msgRectobj.center = End_msgRectobj.move(-_BLOCK_SIZE//2,60).center
    Quit_msg= "Quit"
    Quit_msgSurfaceObj = fontObjbox1.render(Quit_msg,True,whiteColor)
    Quit_msgRectobj = Quit_msgSurfaceObj.get_rect()
    Quit_msgRectobj.center = End_msgRectobj.move(_BLOCK_SIZE,60).center
    if 'fading' not in locals():
        fading = 0  # completely transparent
    while True:
        drawBG(locked,Total)
        if fading <140: fading+=5
        closing.set_alpha(fading)                # alpha level
        closing.fill(lighterblue)               # this fills the entire surface
        windowSurfaceObj.blit(closing, (0,0))    #draw the semi-transparent surface to main surface.
        windowSurfaceObj.blit(End_msgSurfaceObj,End_msgRectobj)
        QuitRect=pygame.draw.rect(windowSurfaceObj,granite,Quit_msgRectobj,0)
        windowSurfaceObj.fill(granite,QuitRect.inflate(15,15))
        windowSurfaceObj.blit(Quit_msgSurfaceObj,Quit_msgRectobj)

        TryRect=pygame.draw.rect(windowSurfaceObj,granite,Try_msgRectobj,0)
        windowSurfaceObj.fill(granite,TryRect.inflate(15,15))
        windowSurfaceObj.blit(Try_msgSurfaceObj,Try_msgRectobj)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                posx, posy= event.pos
                #soundObj.play()
            elif event.type == pygame.QUIT:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                _GameOver= True
                return True
            elif  event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                _GameOver= True
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if Try_msgRectobj.collidepoint((posx, posy)):  #Trying again
                    _GameOver=False
                    return False
                elif Quit_msgRectobj.collidepoint((posx, posy)):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    _GameOver= True
                    return True
        pygame.display.update()
        fpsClock.tick(60)
    return True


locked=[]
action = None
Total = 0
animating = False
animateCounter=0

locked.append( getRandBox(locked))
drawBG(locked,Total)

while not _GameEnd:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  #system (or program) request the game to quit. can do something here for quit
            pygame.quit()
            _GameEnd= True

        elif event.type == pygame.MOUSEMOTION:
            mousex, mousey = event.pos
            #soundObj.play()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if newGameBox.collidepoint((mousex,mousey)):
                print("Starting over")
                locked=[]
                locked.append(getRandBox(locked))
                _2048=None
                Total=0
                drawBG(locked,Total)


        elif event.type == pygame.KEYDOWN:

            if event.key in (pygame.K_LEFT,pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN) :
                original = locked
                locked,animateList,standStill,score=processMovementByMatrix(locked,event.key)
                if not standStill:
                    Total = Total + score
                    new =getRandBox(locked)   #get random box
                    animateNew(new,animateList,original,Total)
                    locked.append(new)       #append to locked
                    print("Score :",Total,"random picK:",new)
                    drawBG(locked,Total)
                    if len(locked)==_SIZE*_SIZE and checkPairable(locked) and not gameEND(False):
                        print("Starting over")
                        locked=[]
                        locked.append(getRandBox(locked))
                        Total=0
                        drawBG(locked,Total)

            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    if _GameOver:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        _GameEnd= True

    if not _GameEnd:
        pygame.display.update()
        fpsClock.tick(60)
