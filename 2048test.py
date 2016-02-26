import pygame
import pygame.locals
import copy
import operator

_SIZE = 4
_BLOCK_SIZE = 100
_MAX = _SIZE*_BLOCK_SIZE
_RIM = 7
_TOP= int(_BLOCK_SIZE*1.5)
fpsClock = pygame.time.Clock()
event2048 = pygame.event.Event(pygame.USEREVENT+1, message="Reach 2048!")
eventAllLocked = pygame.event.Event(pygame.USEREVENT+2, message="All blocks are locked!")
eventNewGame = pygame.event.Event(pygame.USEREVENT+3, message="New Game Started!")


class blocks:
    def __init__(self):
        self.blockList=[]
        self.animatePlan=[]  # either None or Most recent movement plan
        self.score=0
        self.reached2048 = False

    def newBlock(self):
        existing=[]
        if len(self.blockList)>=16:
            raise ValueError("can't have full board")
        for [x,y,z] in self.blockList:
            existing.append(y*_SIZE+x)
        simpleEmpty=[x for x in range(0,16) if x not in existing]
        import random
        x=random.choice(simpleEmpty)
        z = random.randint(0,10)
        z = 2 if z <= 9 else 4
        self.blockList.append([x%4,x//4,z])
        if len(self.blockList)==15 and not self.checkPairable():
            pygame.event.post(eventAllLocked)
        print([x%4,x//4,z])
        return (x%4,x//4,z)
    #takes the myList(which contains the xyz in each block), check if any adjacent blocks are pairable

    def checkPairable(self):

        Matrix = [[0 for x in range(_SIZE)] for x in range(_SIZE)]
        for x,y,z in self.blockList:
            Matrix[y][x]=z
        for j in range(0,_SIZE):
            for i in range(0,_SIZE-1):
                if Matrix [i][j]==Matrix[i+1][j] or Matrix [j][i]==Matrix[j][i+1]:
                    return False #(pairable, no deadlock)
        return True #no pair,

    def moveBlocks(self,directive:int):
        newList=[]
        Matrix = [[[0,x+y*_SIZE] for x in range(_SIZE)] for y in range(_SIZE)]
        for x,y,z in self.blockList:
            Matrix[y][x][0]=z
    #    Here it would had been much easier if i used stack style lists
        if directive == pygame.K_DOWN:  # 90 rotation
            Matrix=[list(elem) for elem in zip(*Matrix[::-1])]
            Matrix,animateList,score=self.addMatrix(Matrix)
            Matrix=[list(elem[::-1]) for elem in zip(*Matrix[::-1])][::-1]
        elif directive == pygame.K_UP:
            Matrix=[list(elem) for elem in zip(*Matrix)]
            Matrix,animateList,score=self.addMatrix(Matrix)
            Matrix=[list(elem) for elem in zip(*Matrix)]

        elif directive == pygame.K_LEFT:  # no rotation
            print('move left, no rotation\n')
            Matrix,animateList,score=self.addMatrix(Matrix)
        elif directive == pygame.K_RIGHT:  # 180 rotation
            print('move right, rotate 180\n')
            Matrix=[each [::-1] for each in Matrix[::-1]]
            Matrix,animateList,score=self.addMatrix(Matrix)
            Matrix=[each [::-1] for each in Matrix[::-1]]

        for j,line in enumerate(Matrix):
            for i,each in enumerate(line):
                if each!=0:
                    newList.append([i,j,each])

        standStill = True if sorted(self.blockList)==sorted(newList) else False
        if standStill :
            animateList.clear()
            directive = 0

        self.blockList.clear()
        self.blockList = list(newList)
        self.score += score
        self.animatePlan = (directive,animateList,self.score,score)

    def addMatrix(self,matrix:list):

        global _2048
        newList=[]
        newLine=[]
        animateList=[]
        score=0
        lastPaired=False
        for line in matrix:
            for counter,[each,i] in enumerate(line):
                if each ==0:
                    pass
                elif len(newLine)>0 and newLine[-1]==each and not lastPaired:

                    if counter < len(newLine) :
                        raise ValueError('height from gravity not higher than blocks underneath')
                    animateList[-1][4]=False
                    animateList.append([i,each,counter-len(newLine),False,True])  # Bool-1:Solid/disappear, Bool-2 = same/double
                    newLine[-1]= 2*each
                    score += 2*each
                    lastPaired=True
                    if  each==1024 and not self.reached2048 :
                        pygame.event.post(event2048)
                else:
                    animateList.append([i,each,counter-len(newLine),True,True])
                    newLine.append(each)
                    lastPaired=False

            lastPaired=False
            newLine.extend( [0] *(_SIZE-len(newLine)))
            newList.append(newLine)
            newLine=[]
        return newList,animateList,score

class graphics:

    def __init__(self):
        
        self.score = 0
        self.white = pygame.Color(255,255,255)
        self.lightBlue = pygame.Color(173, 216, 230)
        self.lighterBlue = pygame.Color(235,255,255)
        self.grey =  pygame.Color(145,141,142)
        self.gold =  pygame.Color(255,215,0)
        self.black=  pygame.Color(0,0,0)
        self.granite = pygame.Color(131,126,124)
        self.colors = {2:(229,228,227),4:(229,228-20,227-40),8:(229,228-30,227-60),16:(229,150,100),
                  32:(200,100,50),64:(150,60,30),128:(255,219,90),
                  256:(229,200,70),512:(229,180,50),1024:(229,170,40),2048:(229,60,20),
                  4096:(60,0,0),8192:(0,0,100),16384:(30,0,0),32768:(0,0,0)}
        for num in range (16,27):
            self.colors[2**num] = (20,0,0)
        self.scoreFont  = pygame.font.Font('AsapBold.ttf',16,bold=True)
        self.menuFont  = pygame.font.Font('AsapBold.ttf',20,bold=True)

        fontObj  = pygame.font.Font('AsapBold.ttf',32,bold= True)
        fontObj2  = pygame.font.Font('AsapBold.ttf',32)
        fontObj16  = pygame.font.Font('AsapBold.ttf',30)
        fontObj128  = pygame.font.Font('AsapBold.ttf',29,bold=True)
        fontObj1024  = pygame.font.Font('AsapBold.ttf',28,bold=True)
        fontObj16384  = pygame.font.Font('AsapBold.ttf',26,bold=True)
        fontObjSmall  = pygame.font.Font('AsapBold.ttf',18,bold=True)

        fonts ={2:fontObj2,4:fontObj2,8:fontObj2,16:fontObj16,32:fontObj16,64:fontObj16,128:fontObj128,256:fontObj128,512:fontObj128,
                1024:fontObj1024,2048:fontObj1024,4096:fontObj1024,8192:fontObj1024,16384:fontObj16384,0:fontObjSmall}
        #3 ways of creating dictionary. 1. assign one-by-one. 2. from tuples. 3 from parallel lists (straight forward)
        self.menuTitleFont=pygame.font.Font('AsapBold.ttf',34,bold= True)
        self.fontBox={}
        for num in range(1,27):
            self.fontBox[2**num]=fonts.get(2**num,fonts[0]).render(str(2**num),True,self.granite if 2**num<16 else self.white)

        self.paintedBlocks= {}
        for num in range(1,27):
            self.paintedBlocks[2**num] = pygame.Surface((_BLOCK_SIZE-_RIM,_BLOCK_SIZE-_RIM))
            self.paintedBlocks[2**num].fill(self.colors[2**num])
            numRect = self.fontBox[2**num].get_rect()
            numRect.center = self.paintedBlocks[2**num].get_rect().center
            self.paintedBlocks[2**num].blit(self.fontBox[2**num],numRect)

        self.fontBox[0]=fonts[0].render(str(2**num),True,self.white)
        self.fontBox[-1]=self.menuFont.render('New Game',True,self.white)
        self.fontBox[-2]=self.scoreFont.render('Best',True,self.grey)
        self.fontBox[-3]=self.scoreFont.render('Score',True,self.grey)
        titleBox = fontObj.render('2048',True,self.white)

        self.fontBox[1]=fonts[0].render(str(2**num),True,self.grey)


        self.boxArea=pygame.Surface((_BLOCK_SIZE*_SIZE,int(_BLOCK_SIZE*(_SIZE+1.5))))
        self.boxArea.fill(self.lightBlue)
        self.topArea=pygame.Surface((_BLOCK_SIZE*2,_BLOCK_SIZE*1.5))

        topRect=self.topArea.get_rect()
        self.topArea.fill(self.lightBlue)
        x,y = topRect.center

        scoreRect = pygame.Rect(0,0,_BLOCK_SIZE-_RIM,int(_BLOCK_SIZE*.6))
        bestRect = pygame.Rect(0,0,_BLOCK_SIZE-_RIM,int(_BLOCK_SIZE*.6))
        ngRect = pygame.Rect(0,0,int(1.3*_BLOCK_SIZE),_BLOCK_SIZE//2)
        scoreRect.centery = bestRect.centery = y + int(_BLOCK_SIZE//2.5)
        scoreRect.centerx = x - _BLOCK_SIZE//2
        bestRect.centerx = x + _BLOCK_SIZE//2
        ngRect.centerx = x
        ngRect.centery = int(_BLOCK_SIZE//2.5)

        boxRect = self.boxArea.get_rect()
        topRect.right=boxRect.right
        topRect.top = boxRect.top
        self.scorePos=(boxRect.right-2*_RIM,topRect.bottom-2*_RIM)
        self.bestPos=(boxRect.right-2*_RIM-_BLOCK_SIZE,topRect.bottom-2*_RIM)

        ngwidth = self.fontBox[-1].get_rect().width

        titleRect = titleBox.get_rect()
        titleRect.center = (_BLOCK_SIZE,_BLOCK_SIZE//2)
        pygame.draw.rect(self.boxArea,self.black,titleRect.inflate(40,20),1)
        pygame.draw.rect(self.topArea,self.grey,scoreRect,1)
        pygame.draw.rect(self.topArea,self.grey,bestRect,1)
        pygame.draw.rect(self.topArea,self.black,ngRect,1)


        self.topArea.fill(self.colors[8],scoreRect.inflate(-1,-1))
        self.topArea.fill(self.colors[8],bestRect.inflate(-1,-1))
        self.topArea.fill(self.granite,ngRect.inflate(-1,-1))

        self.boxArea.blit(titleBox,titleRect)

        self.topArea.blit(self.fontBox[-1],(ngRect.x+int(1.25*_BLOCK_SIZE-ngwidth)//2,ngRect.centery//2+_RIM))
        self.topArea.blit(self.fontBox[-2],(scoreRect.x+5,scoreRect.y+3))
        self.topArea.blit(self.fontBox[-3],(bestRect.x+5,bestRect.y+3))


        self.boxArea.blit(self.topArea,topRect)
        for y in range(0,_SIZE):
            for x in range(0,_SIZE):
                pygame.draw.rect(self.boxArea,self.lighterBlue, self.makeRect(x,y,_BLOCK_SIZE-_RIM))
        self.bgArea=self.boxArea.copy()

    def makeRect(self,x,y,side ):
        newRect= pygame.Rect(0,0,side,side)
        newRect.centerx = x*_BLOCK_SIZE +_BLOCK_SIZE//2
        newRect.centery = _TOP+ y*_BLOCK_SIZE +_BLOCK_SIZE//2
        return newRect

    def updateScore(self,score):
        msg=str(score)
        scoreCounterBoxObj = self.scoreFont.render(msg,True,self.white)
        bestCounterBoxObj = self.scoreFont.render(msg,True,self.white)
        scoreBox= scoreCounterBoxObj.get_rect()
        bestBox = bestCounterBoxObj.get_rect()
        scoreBox.right,scoreBox.bottom = self.scorePos
        bestBox.right,bestBox.bottom = self.bestPos
        self.boxArea.fill(self.colors[8],scoreBox)
        self.boxArea.fill(self.colors[8],bestBox)
        self.boxArea.blit(scoreCounterBoxObj,scoreBox)
        self.boxArea.blit(bestCounterBoxObj,bestBox)
    def updateScoreBG(self,score):
        msg=str(score)
        scoreCounterBoxObj = self.scoreFont.render(msg,True,self.white)
        bestCounterBoxObj = self.scoreFont.render(msg,True,self.white)
        scoreBox= scoreCounterBoxObj.get_rect()
        bestBox = bestCounterBoxObj.get_rect()
        scoreBox.right,scoreBox.bottom = self.scorePos
        bestBox.right,bestBox.bottom = self.bestPos
        self.bgArea.fill(self.colors[8],scoreBox)
        self.bgArea.fill(self.colors[8],bestBox)
        self.bgArea.blit(scoreCounterBoxObj,scoreBox)
        self.bgArea.blit(bestCounterBoxObj,bestBox)
    def drawBox(self,box):
        x,y,z=box
        rectPos = self.makeRect(x,y,_BLOCK_SIZE-_RIM)
        self.boxArea.blit(self.paintedBlocks[z],rectPos)
    def animateMoveBlocks(self,animatePlan):

        directive,animateList,addedscore,score=animatePlan
        if directive == 0 :
            return []
        flickPerBlock=4  #4 ticks per block

        animateCounter=_SIZE*flickPerBlock
        step =  _BLOCK_SIZE//animateCounter #for new blocks and double blocks

        screenList= []
        self.updateScoreBG(addedscore)
        for i in range(0,animateCounter):
            screenList.append(self.bgArea.copy())
        if score > 0 : self.animateScore(screenList,score)

        for i,[ pos,value,move,willStaySolid,willNumFixed] in enumerate(animateList):
            x1,y1=pos%_SIZE,pos//_SIZE  # for all blocks except new
            tempRect= self.makeRect(x1,y1,_BLOCK_SIZE-_RIM)
            screenList[0].blit(self.paintedBlocks[value],tempRect)

            if willStaySolid and willNumFixed and move == 0:
                for frame in range(1,animateCounter):
                    screenList[frame].blit(self.paintedBlocks[value],tempRect)
            elif willStaySolid and willNumFixed:
                for frame in range(1,move*flickPerBlock+1):
                    tempRect.center = graphics.boxShift(tempRect.center,directive,flickPerBlock)
                    screenList[frame].blit(self.paintedBlocks[value],tempRect)

                for frame in range(move*flickPerBlock+1,animateCounter):
                    screenList[frame].blit(self.paintedBlocks[value],tempRect)

            elif not willStaySolid and not willNumFixed:
                raise ValueError('cant have both: vanishing and doubling')
            elif not willStaySolid:
                for frame in range(1,move*flickPerBlock):
                    tempRect.center = graphics.boxShift(tempRect.center,directive,flickPerBlock)
                    screenList[frame].blit(self.paintedBlocks[value],tempRect)
            elif not willNumFixed:
                for frame in range(1,move*flickPerBlock+1):
                    tempRect.center = graphics.boxShift(tempRect.center,directive,flickPerBlock)
                    screenList[frame].blit(self.paintedBlocks[value],tempRect)

                growing = _BLOCK_SIZE//2+1  #starting size for double block
                for frame in range(animateCounter//2,animateCounter):   # generate frames for double block with zoom fx
                    tmpx,tmpy=graphics.boxMove(x1,y1,directive,move)
                    tempRect=self.makeRect(tmpx,tmpy,growing)
                    growing = growing+step
                    self.drawRect(screenList[frame],tempRect,value*2)

        self.boxArea=screenList[-1]
        return screenList

    def animateNewBlock(self,newBox,frameList):
        x,y,z=newBox
        animateCounter = len(frameList)
        step =  _BLOCK_SIZE//animateCounter

        growing = _BLOCK_SIZE//2+1  # starting size for the one new block
        for frame in range(animateCounter//2,animateCounter):  #generate frames for the one new block with zoom fx
            tempRect=self.makeRect(x,y,growing)
            growing = growing+step
            self.drawRect(frameList[frame],tempRect,z)

        pygame.draw.rect(frameList[-1],self.gold, tempRect)
        pygame.draw.rect(frameList[-1],self.colors[z], tempRect.inflate(-4,-4))
        tempFont = self.fontBox[z].get_rect()
        tempFont.center = tempRect.center

        frameList[-1].blit(self.fontBox[z],tempFont)

        self.boxArea=frameList[-1]

    def animateScore(self,frameList,score):
        animateCounter = len(frameList)
        msg=str(score)
        scoreBoxObj = self.scoreFont.render(msg,True,self.white)
        bestBoxObj = self.scoreFont.render(msg,True,self.white)
        scoreBox= scoreBoxObj.get_rect()
        bestBox = bestBoxObj.get_rect()
        scoreBox.right,scoreBox.bottom = self.scorePos
        bestBox.right,bestBox.bottom = self.bestPos
        bestBox.bottom-=5
        scoreBox.bottom -=5
        step = 3
        for frame in range(animateCounter//2,animateCounter):  #generate frames for the one new block with zoom fx
            frameList[frame].fill(self.colors[8],scoreBox)
            frameList[frame].fill(self.colors[8],bestBox)
            frameList[frame].blit(scoreBoxObj,scoreBox)
            frameList[frame].blit(bestBoxObj,bestBox)
            bestBox.bottom-=step
            scoreBox.bottom -=step
        frameList[-1].fill(self.colors[8],scoreBox)
        frameList[-1].fill(self.colors[8],bestBox)

    def drawRect(self,screen,boxRect,value,color=None):
        myRect=pygame.draw.rect(screen,self.colors[value], boxRect)
        msgRectObj = self.fontBox[value].get_rect()
        msgRectObj.center = myRect.center
        screen.blit(self.fontBox[value],msgRectObj)

    @staticmethod
    def boxShift(boxRect,directive,shift):
        Shifter={pygame.K_DOWN:(0,+_BLOCK_SIZE//shift),pygame.K_UP:(0,-_BLOCK_SIZE//shift),
                 pygame.K_LEFT:(-_BLOCK_SIZE//shift,0),pygame.K_RIGHT:(+_BLOCK_SIZE//shift,0)}
        return tuple(map(operator.add,boxRect, Shifter[directive]))
    @staticmethod
    def boxMove(x1,y1,directive,move):
        if directive in (pygame.K_DOWN, pygame.K_UP):
            y1+= move if directive == pygame.K_DOWN else -move
        elif directive in (pygame.K_LEFT, pygame.K_RIGHT):
            x1+= move if directive == pygame.K_RIGHT else -move
        if x1 >=_SIZE or x1<0 or y1>= _SIZE or y1<0 : raise ValueError('block beyond boundaries')
        return x1,y1  # trivia: return type is tuple here


def closeMenu(mainScreen,gameData,gameGraphics,eventNum):
    animateCounter=25
    posx,posy = 0,0
    menuLayer = pygame.Surface([_MAX,_MAX+_TOP])  # the size of your rect
    menuLayer2 = pygame.Surface([_MAX,_MAX+_TOP])  # the size of your rect
    menuLayer2.fill(gameGraphics.lightBlue)
    midPoint = menuLayer.get_rect().center
    midPointX, midPointY = midPoint
    upCenter = (midPointX,midPointY-_BLOCK_SIZE//2)
    leftBottomCenter = (midPointX-_BLOCK_SIZE,midPointY+_BLOCK_SIZE//3)
    rightBottomCenter = (midPointX+.9*_BLOCK_SIZE,midPointY+_BLOCK_SIZE//3)

    buttonRect = pygame.Rect(0,0,int(1.3*_BLOCK_SIZE),_BLOCK_SIZE//2)
    topMsg=leftMsg=rightMsg=None
    if eventNum == eventAllLocked.type:
        topMsg = "Game Over!"
        leftMsg = "Try Again?"
        rightMsg = "Quit"
    elif eventNum == event2048.type:
        topMsg = "You Won!"
        leftMsg = "Continue"
        rightMsg = "Quit"
    elif eventNum == eventNewGame.type:
        topMsg = "New Game?"
        leftMsg = "Yes"
        rightMsg = "Continue"

    print(topMsg,leftMsg,rightMsg)

    topMsgSurface = gameGraphics.menuTitleFont.render(topMsg,True,gameGraphics.white)
    topRect=topMsgSurface.get_rect()
    topRect.midbottom = upCenter
    
    leftMsgSurface = gameGraphics.menuFont.render(leftMsg,True,gameGraphics.white)
    leftRect = leftMsgSurface.get_rect()
    leftRect.midbottom = leftBottomCenter
    
    rightMsgSurface = gameGraphics.menuFont.render(rightMsg,True,gameGraphics.white)
    rightRect = rightMsgSurface.get_rect()
    rightRect.midbottom = rightBottomCenter

    buttonRect.center = leftRect.center
    menuLayer.fill(gameGraphics.colors[8],buttonRect)

    buttonRect.center = rightRect.center
    menuLayer.fill(gameGraphics.colors[8],buttonRect)

    menuLayer.blit(topMsgSurface,topRect)
    menuLayer.blit(leftMsgSurface,leftRect)
    menuLayer.blit(rightMsgSurface,rightRect)


    bgLayer2 = mainScreen.copy()
    startA=50
    endA = 180
    step = (180-50)/(2*60)
    i=startA


    while True:
        if i < endA:
            bgLayer = bgLayer2.copy()
            menuLayer2.set_alpha(i)
            bgLayer.blit(menuLayer2,(0,0))
            bgLayer.blit(menuLayer,(0,0))
            mainScreen.blit(bgLayer,(0,0))
            i += step
        pygame.display.flip()
        fpsClock.tick(60)
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
                if leftRect.collidepoint((posx, posy)):  #Trying again
                    _GameOver=False
                    return False
                elif rightRect.collidepoint((posx, posy)):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    _GameOver= True
                    return True
    '''while True:
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
        fpsClock.tick(60)'''
    return True


pygame.init()
mainScreen= pygame.display.set_mode((_MAX,_MAX+150))
pos  = mainScreen.get_rect()

pygame.display.set_caption('2048')

gameBG = graphics()
gameBG.updateScore(0)
gameDATA = blocks()
gameDATA.newBlock()
#gameBG.boxArea.fill(lightblue)
pygame.event.post(eventNewGame)
#closeMenu(mainScreen,gameDATA,gameBG,pygame.USEREVENT+1)
while  1:
    mainScreen.blit(gameBG.boxArea,pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  #system (or program) request the game to quit. can do something here for quit
            pygame.quit()
            _GameEnd= True

        elif event.type == pygame.MOUSEMOTION:
            mousex, mousey = event.pos
            #soundObj.play()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if  True:   #newGameBox.collidepoint((mousex,mousey)):
                print("Starting over")
                #locked.append(getRandBox(locked))
                _2048=None
                Total=0
                #drawBG(locked,Total)
                #gameDATA.newBlock()

        elif event.type == pygame.KEYDOWN:

            if event.key in (pygame.K_LEFT,pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN) :

                gameDATA.moveBlocks(event.key)
                frameList=gameBG.animateMoveBlocks(gameDATA.animatePlan)

                if len(frameList) > 0 :
                    newBox = gameDATA.newBlock()
                    gameBG.animateNewBlock(newBox,frameList)

                    for each in frameList:
                        mainScreen.blit(each,pos)
                        pygame.display.flip()
                        fpsClock.tick(60)
                if gameDATA.score > 50:
                    closeMenu(mainScreen,gameDATA,gameBG,pygame.USEREVENT+1)

                #mainScreen.blit(gameBG.boxArea,pos)

                #locked,animateList,standStill,score=processMovementByMatrix(locked,event.key)
                '''if not standStill:
                    Total = Total + score
                    #new =getRandBox(locked)   #get random box
                    #animateNew(new,animateList,original,Total)
                    locked.append(new)       #append to locked
                    print("Score :",Total,"random picK:",new)
                    #drawBG(locked,Total)
                    if len(locked)==_SIZE*_SIZE and checkPairable(locked) and not gameEND(False):
                        print("Starting over")
                        locked=[]
                        locked.append(getRandBox(locked))
                        Total=0
                        drawBG(locked,Total)'''

            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
    pygame.display.flip()
    fpsClock.tick(30)
