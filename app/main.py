import bottle
import os
import networkx as nx
import numpy as np
import random


class Snake(object):
    def __init__(self,newName,row,col,unique=1,method = 'a_star',a = 0.7,b = 0.7,c = 0.1):
        self.legendString = '~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQURTUVWXYZ!@#$%^&*()_+<>?:"{}|\][/.,'
        self.legendMatrix = []
        self.n = row
        self.rows = row
        self.cols = col
        #self.walls = self.generateWalls()
        self.id = unique
        self.method = method
        self.name = newName
        self.hunger = 100
        self.a = a
        self.b = b
        self.c = c
        self.gameID = ''
        for row in range(self.rows):
            for col in range(self.cols):
                self.legendMatrix.append(self.legendString[row]+self.legendString[col])
        self.legendMatrix = np.asarray(self.legendMatrix)
        self.G = nx.Graph()
        self.G.add_nodes_from(self.legendMatrix)
        self.legendMatrix = self.legendMatrix.reshape((self.rows,self.cols))

    def addBarriers(self,beforeFrame,toAdd):
        localFrame = np.copy(beforeFrame)
        
        for coords in range(len(toAdd)):
            if(coords==0):
                localFrame[toAdd[coords][0],toAdd[coords][1]] = 5
            else:
                localFrame[toAdd[coords][0],toAdd[coords][1]] = 1
        
        #localFrame
        return localFrame
	
	
				
		
			
    '''
    def generateWalls(self):
        output_args = np.ones((self.rows,self.cols))
        output_args[0:self.rows,0:self.cols] = np.zeros((self.rows,self.cols))
        return output_args
	'''
    
    def makeDecision(self):
        try:
            if(self.path==''):
                return 'up'
            if(len(self.path)==1):
                return 'down'
            try:
                if(self.path[1]==self.legendMatrix[self.snakeHead[0]+1,self.snakeHead[1]]):
                    return 'right'#was up
            except Exception as e:
                pass
            try:
                if(self.path[1]==self.legendMatrix[self.snakeHead[0]-1,self.snakeHead[1]]):
                    return 'left'#was down
            except Exception as e:
                pass
            try:
                if(self.path[1]==self.legendMatrix[self.snakeHead[0],self.snakeHead[1]+1]):
                    return 'down'#was right
            except Exception as e:
                pass
            try:
                if(self.path[1]==self.legendMatrix[self.snakeHead[0],self.snakeHead[1]-1]):
                    return 'up'#was left
            except Exception as e:
                pass
        except Exception as e:
            print 'DECISION ERROR: '+ e.message
            print 'snakeHead: '
            print self.snakeHead
            print 'Path:%s'%(self.path)
            print 'Path Length:%d'%(len(self.path))
          
    
    def generateDanger(self):
        self.weights = np.zeros((self.rows,self.cols))
        for row in range(0,self.rows):
            for col in range(0,self.cols):
                try:
                    #self.weights[row,col] = 1
                    self.weights[row,col] = self.currentFrame[row,col]*self.b+self.c + self.currentFrame[row+1,col]*self.b+self.currentFrame[row-1,col]*self.b+self.currentFrame[row,col+1]*self.b+self.currentFrame[row,col-1]*self.b
                except Exception as e:
                    pass
        self.weights = self.weights#+self.walls
        
    def generateMoveset(self):
        for row in range(self.rows):
            for col in range (self.cols):
                if(row+1< self.rows): #make sure I dont go out of bounds
                    if(self.currentFrame[row,col]==0 and self.currentFrame[row+1,col]==0):
                        self.G.add_edge(self.legendMatrix[row,col],self.legendMatrix[row+1,col], weight = (self.weights[row,col]*self.a + self.weights[row+1,col]*self.b))
                if(row-1>0):        
                    if(self.currentFrame[row,col]==0 and self.currentFrame[row-1,col]==0):
                        self.G.add_edge(self.legendMatrix[row,col],self.legendMatrix[row-1,col], weight = (self.weights[row,col]*self.a + self.weights[row-1,col]*self.b))
                if(col+1<self.cols):
                    if(self.currentFrame[row,col]==0 and self.currentFrame[row,col+1]==0):
                        self.G.add_edge(self.legendMatrix[row,col],self.legendMatrix[row,col+1], weight = (self.weights[row,col]*self.a + self.weights[row,col+1]*self.b))
                if(col-1>0):
                    if(self.currentFrame[row,col]==0 and self.currentFrame[row,col-1]==0):
                        self.G.add_edge(self.legendMatrix[row,col],self.legendMatrix[row,col-1], weight = (self.weights[row,col]*self.a + self.weights[row,col-1]*self.b))
                if(self.currentFrame[row,col]!=0):
                    try:
                        self.G.remove_edge(self.legendMatrix[row,col],self.legendMatrix[row+1,col])
                    except Exception:
                        pass
                    try:
                        self.G.remove_edge(self.legendMatrix[row,col],self.legendMatrix[row-1,col])
                    except Exception:
                        pass
                    try:
                        self.G.remove_edge(self.legendMatrix[row,col],self.legendMatrix[row,col+1])
                    except Exception:
                        pass
                    try:
                        self.G.remove_edge(self.legendMatrix[row,col],self.legendMatrix[row,col-1])
                    except Exception:
                        pass
        
    
    
    def dist(self,start,finish):
        deltaX = np.linalg.norm([start[0],finish[0]])
        deltaY = np.linalg.norm([start[1],finish[1]])
        return np.linalg.norm([deltaX,deltaY])
        
    def calcDist(self,unsorted):
        ans= np.array([])
        for uns in unsorted: 
            dx = uns[0]-self.snakeHead[0]
            dy = uns[1]-self.snakeHead[1]
            temp = [pow(pow(dx,2)+pow(dy,2),0.5)]
            ans=np.append(ans,temp)
        return ans
    def generateSnakeWalls(self, turn, snakeList): #snakeList: snakes list
        boardXlen = self.rows
        boardYlen = self.cols
        board = []
        for i in range(boardXlen):
            board.append([])
            for j in range(boardYlen):
                board[i].append(0)
                for snake in snakeList:
                    snake_len = len(snake['coords'])
                    snake_id = snake['id']
                    coords = snake['coords']
                    if turn == 0:
                        board[coords[0][0]][coords[0][1]] = ['H', snake_id]
                    elif turn == 1:
                        board[coords[0][0]][coords[0][1]] = ['H', snake_id]
                        board[coords[1][0]][coords[1][1]] = [2, snake_id]
                    else:
                        for i in range(snake_len):
                            if i == 0:
                                board[coords[i][0]][coords[i][0]] = ['H', snake_id]
                            else:
                                board[coords[i][0]][coords[i][1]] = [snake_len-i, snake_id]			
        return board
    
    def lookup(self,node):
        for row in range(self.rows):
            for col in range(self.cols):
                if(node==self.legendMatrix[row,col]):
                    return (row,col)

    def kom(self,path):
        localG=  self.G
        if(path!=''):
            (endingrow,endingcol) = self.lookup(path[-1])
            for node in path:
                (localrow,localcol) = self.lookup(node)
                try:
                    localG.remove_edge(node,self.legendMatrix[localrow+1,localcol])
                except Exception as e:
                    pass
                try:
                    localG.remove_edge(node,self.legendMatrix[localrow-1,localcol])
                except Exception as e:
                    pass
                try:
                    localG.remove_edge(node,self.legendMatrix[localrow,localcol+1])
                except Exception as e:
                    pass
                try:
                    localG.remove_edge(node,self.legendMatrix[localrow,localcol-1])
                except Exception as e:
                    pass
            #all nodes to the path are now removed. Test to see if I can get back to my tail
            points = np.array([[self.snakeBody[-1,0],self.snakeBody[-1,1]]])
            points = np.append(points,[[self.snakeBody[-1,0]+1,self.snakeBody[-1,1]]],0)
            points = np.append(points,[[self.snakeBody[-1,0]-1,self.snakeBody[-1,1]]],0)
            points = np.append(points,[[self.snakeBody[-1,0],self.snakeBody[-1,1]+1]],0)
            points = np.append(points,[[self.snakeBody[-1,0],self.snakeBody[-1,1]-1]],0)
            for point in points:
                try:
                    nx.astar_path(localG,self.legendMatrix[endingrow,endingcol],self.legendMatrix[point[0],point[1]])
                    return True #if it reaches this it hasnt errored out therefore there is a path
                except Exception as e:
                    pass
                finally:
                    return False #if it reaches this it has killed itself, dont do it

    
    def checkFood(self,points):
        itemsToRemove =[]
        for snek in data['snakes']:
            if(snek['name']!='Vengeful Mittens'):
                body = snek['coords']
                head = body[0]
                for point in range(len(points)):
                    try:
                        dx = point[0]-head[0]
                        dy = point[1]-head[1]
                        temp = pow(pow(dx,2)+pow(dy,2),0.5)
                        if(temp==1):
                            itemsToRemove.append(point)
    #        np.delete(points,itemsToRemove,axis=0)
        return points
        
            
    def turn(self,data):
        self.alldata = data
        #wallBoard = self.generateSnakeWalls(data['turn'],data['snakes'])
        
        unsortedFood = np.copy(data['food'])
        self.food = np.copy(data['food'])
        self.hunger -=1                 # loose a hunger, cause a turn has passed
        self.a = self.hunger/100.0
        self.b = self.hunger/100.0
        localSnakes = data['snakes']   # make sure we dont change the orignal
        self.currentFrame = np.zeros((self.rows,self.cols))
        for snek in localSnakes:
            self.currentFrame = self.addBarriers(self.currentFrame,snek['coords'])
            if snek['name']=='Vengeful Mittens':
                snake = snek['coords']    # isolate just our snake from all the snakes
                allsnakeData = snek
        
        
        self.snakeHead = snake[0]                                   # set the snake head to the first thing in the snake array
        self.currentFrame[self.snakeHead[0],self.snakeHead[1]]=0    # make sure the head is not 1! EXTREMEMLY IMPORTANT
        snake = np.roll(snake,-1,0)     # circular shift, put the head at the back of the array
        self.snakeBody = snake[:-1]          # copy everything but the head
        self.generateDanger()           # generate the danger matrix
        self.generateMoveset()          # generate the moveset
        self.path = ''

        
        index = 0
        while len(unsortedFood)!=0:
            distanceFood = self.calcDist(unsortedFood)
            maxFood = np.argmin(distanceFood)
            self.food[index]=unsortedFood[maxFood]
            unsortedFood = np.delete(unsortedFood,maxFood,0)
            index+=1
         
        points = np.array(self.food.tolist())
        point = self.checkFood(points)
        if(len(points)!=0):
            points = np.append(points,[[self.snakeBody[-1,0],self.snakeBody[-1,1]]],0)
        else:
            points = np.array([[self.snakeBody[-1,0],self.snakeBody[-1,1]]])
        points = np.append(points,[[self.snakeBody[-1,0]+1,self.snakeBody[-1,1]]],0)
        points = np.append(points,[[self.snakeBody[-1,0]-1,self.snakeBody[-1,1]]],0)
        points = np.append(points,[[self.snakeBody[-1,0],self.snakeBody[-1,1]+1]],0)
        points = np.append(points,[[self.snakeBody[-1,0],self.snakeBody[-1,1]-1]],0)
        
        
        for point in points:
            if self.method == 'a_star':
                try:
                    self.path =  nx.astar_path(self.G,self.legendMatrix[self.snakeHead[0],self.snakeHead[1]],self.legendMatrix[point[0],point[1]])
                    if(self.kom(self.path)):
                        return self.makeDecision()
                    break
                except Exception as e:
                    #print self.name + '-> Tail Exception: '+ e.message
                    pass
            if self.method =='dijkstra_path':
                try:
                    self.path =  nx.dijkstra_path(self.G,self.legendMatrix[self.snakeHead[0],self.snakeHead[1]],self.legendMatrix[point[0],point[1]])
                    return self.makeDecision()
                    break
                except Exception as e:
                    #print self.name + '-> Tail Exception: '+ e.message
                    pass
        return self.makeDecision()
      



@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.get('/')
def index():
    #head_url = '%s://%s/static/head.png' % (
    #    bottle.request.urlparts.scheme,
    #    bottle.request.urlparts.netloc
    #)
    
    
    return {
        'color': '#ffffff',
        'head': 'fang'
    }


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']
    
    
    

    #head_url = '%s://%s/static/head.png' % (
    #    bottle.request.urlparts.scheme,
    #    bottle.request.urlparts.netloc
    #)
    return {
        'color': '#00ff00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': 'fang',
        'name': 'Vengeful Mittens'
    }



@bottle.post('/move')
def move():
    data = bottle.request.json 
    try:
        snek = Snake(data['game_id'],data['width'],data['height'])
        move = snek.turn(data)
        taunt = 'W:%s'%(move)
    except Exception as e:
        move = random.choice(['up','down','left','right'])
        taunt = e.message
        

    return {
        'move': move,
        'taunt': taunt
    }


@bottle.post('/end')
def end():
    data = bottle.request.json

    # TODO: Do things with data

    return {
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    global snakes
    snakes=[]
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
