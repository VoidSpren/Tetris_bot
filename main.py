import pyautogui as ag
from PIL import Image, ImageOps
import numpy as np
import numpy.typing as npt
import time
import math
import os

from tetrisPieces import pieces

ag.PAUSE = 0

# movements = {"l": "left", "r": "rigth", "d":"down", "CW": "x", "CCW": "z", "drop": "space", "180": "A", "no":""}
movements = ["left", "right", "down", "up", "ctrl", "space", "a", ""]

# inverted = {"l": "r", "r": "l", "u":"d", "CW": "CCW", "CCW": "CW", "undrp": "drop", "180": "180", "no": "no"}
# inverted = [1, 0, 2, 4, 3, 5, 6, 7]

log = open("log.txt", "w")


class AgenteTetris:
  def __init__(self) -> None:
    self.rows = 20
    self.columns = 10
    self.minRow = 2
    self.savedPiece: int = None

  def getRow(self, row: int):
    return row + self.minRow
  
  def getShape(self, board: npt.NDArray[np.uint8]) -> int:
    shape = np.zeros((2, 4), dtype=np.uint8)

    pieceIndex = -1

    print(board, file=log)

    for y in range(2):
      for x in range(4):
        shape[y, x] = board[y, x + 3]
        board[y, x + 3] = 0
    
    print(shape, file=log)
    
    for i in range(len(pieces)):
      equal = True

      if(i < (len(pieces) -1)):
        for y in range(2):
          for x in range(4):
            squares = (shape[y,x] == pieces[i][0][y + 1][x])
            if(not squares):
              equal = False
      else:
        for y in range(1):
          for x in range(4):
            squares = (shape[y + 1 ,x] == pieces[i][0][y + 1][x])
            if(not squares):
              equal = False
      
      if(equal):
        pieceIndex = i
        break
    
    print(pieceIndex, file=log)

    return pieceIndex
  
  def checkCollision(self, x: int, y: int, r: int, piece: int, board: npt.NDArray[np.uint8]):
    for i in range(4):
      row = y + i

      for j in range(4):
        column = x + j

        if(pieces[piece][r][i][j] == 1 and
           (row >= self.rows or row < -2 or
            column >= self.columns or column < 0 or
            board[self.getRow(row), column] == 1)):
          
          return True
    
    return False
  
  
  def checkFloor(self, x: int, y: int, r: int, piece: int, board: npt.NDArray[np.uint8]):

    for i in reversed(range(4)):
      for j in range(4):
        if(pieces[piece][r][i][j] == 1):
          row = i + y + 1 
          if(row >= self.rows or (row > 0 and board[self.getRow(row), j + x] == 1)):
            return True
    return False

  def checkCollisionAndFloor(self, x: int, y: int, r: int, piece: int, board: npt.NDArray[np.uint8]):
    floor = False

    for i in range(4):
      row = y + i

      for j in range(4):
        column = x + j

        if(pieces[piece][r][i][j] == 1):
           
          if( row >= self.rows or row < -2 or
              column >= self.columns or column < 0 or
              board[self.getRow(row), column] == 1):
          
            return [True, floor]
          elif(not floor):
            floorRow = row + 1
            if (floorRow >= self.rows or (floorRow > 0 and board[self.getRow(floorRow), column] == 1)):
              floor = True
    
    return [False, floor]
  
  
  def findPlaceAbleSpaces(self, board: npt.NDArray[np.uint8], piece: int):
    placeAble = []

    for y in reversed(range(-2, self.rows - 1)):
      for x in range(-2, self.columns - 1):
        for rot in range(4):
          res = self.checkCollisionAndFloor(x, y, rot, piece, board)
          if((not res[0]) and res[1]):
            placeAble.append((x, y, rot))

    return placeAble
  
  def createPossibleNodes(self, piece: int, current: tuple[int, int, int], board: npt.NDArray[np.uint8]):
    # inverted = {"l": "r", "r": "l", "u":"d", "CW": "CCW", "CCW": "CW", "undrp": "drop", "180": "180", "no": "no"}
# inverted = [1, 0, 2, 4, 3, 5, 6, 7]
    nodes: list = []
    if(not self.checkCollision(current[0] + 1, current[1], current[2], piece, board)):
      # nodes.append({"act":"r", "pos": (current[0] + 1, current[1], current[2]), "cost": 1.0})
      nodes.append([0, (current[0] + 1, current[1], current[2]), 1.0])
    if(not self.checkCollision(current[0] - 1, current[1], current[2], piece, board)):
      # nodes.append({"act":"l", "pos": (current[0] - 1, current[1], current[2]), "cost": 1.0})
      nodes.append([1, (current[0] - 1, current[1], current[2]), 1.0])
    if(not self.checkCollision(current[0], current[1] - 1, current[2], piece, board)):
      # nodes.append({"act":"u", "pos": (current[0], current[1] - 1, current[2]), "cost": 1.0})
      nodes.append([2, (current[0], current[1] - 1, current[2]), 1.0])
    if(not self.checkCollision(current[0], current[1], (current[2] + 1)%4, piece, board)):
      # nodes.append({"act":"CW", "pos": (current[0], current[1], (current[2] + 1)%4), "cost": 1.5})
      nodes.append([4, (current[0], current[1], (current[2] + 1)%4), 1.5])
    if(not self.checkCollision(current[0], current[1], (current[2] - 1)%4, piece, board)):
      # nodes.append({"act":"CCW", "pos": (current[0], current[1], (current[2] - 1)%4), "cost": 1.5})
      nodes.append([3, (current[0], current[1], (current[2] - 1)%4), 1.5])
    if(not self.checkCollision(current[0], current[1], (current[2] + 2)%4, piece, board)):
      # nodes.append({"act":"180", "pos": (current[0], current[1], (current[2] + 2)%4), "cost": 1.5})
      nodes.append([6, (current[0], current[1], (current[2] + 2)%4), 1.5])

    return nodes
  
  def AstarHeur(self, finnish: tuple[int, int, int], node: tuple[int, int, int], gScore: float) -> float: 
    return abs(node[0] - finnish[0]) + abs(node[1] - finnish[1]) + (1.5 if (node[2] != finnish[2]) else 0) + gScore


  def AStar(self, piece: int, start: tuple[int, int, int], board: npt.NDArray[np.uint8]):
    #startNode = {"act": "no", "pos": start, "cost": 0.0, "id": 0}
    startNode = [7, start, 0.0, 0]

    finnish: tuple[int, int, int] = None
    if(piece == len(pieces) - 1):
      finnish = (3, -2, 0)
    else:
      finnish = (3, -3, 0)
    

    opList = [0]
    fromList = []


    nodeIndexes = [start]
    nodes = [startNode]
    gScores= [0.0]
    fScores = [self.AstarHeur(finnish, startNode[1], 0.0)]

    while(len(opList) > 0):

      # print("op")

      # costs = map(lambda node: self.AstarHeur(finnish, node, totalCost), opList)
      costs = [[i, fScores[i]] for i in opList]
      indexCost = -1
      minCost = math.inf
      for i in range(len(costs)):
        if(costs[i][1] < minCost):
          indexCost = i
          minCost = costs[i][1]
      
      currentIndex = costs[indexCost][0]
      current = nodes[currentIndex]

      if(current[1] == finnish):
        fromList.append(current)
        return fromList
      
      opList.remove(currentIndex)
      neigbours = self.createPossibleNodes(piece, current[1], board)
      for i in neigbours:

        tentGScore = gScores[currentIndex] + i[2]
        try:
          nodeIndex = nodeIndexes.index(i[1])
          gScore = gScores[nodeIndex]

          if(gScore > tentGScore):
            fromList[nodeIndex - 1] = current
            gScores[nodeIndex] = tentGScore
            fScores[nodeIndex] = self.AstarHeur(finnish, i[1], tentGScore)

            nodes[nodeIndex] = i
            if nodeIndex not in opList:
              opList.append(nodeIndex)

        except ValueError:
          nodeIndex = len(nodeIndexes)
          i.append(nodeIndex)
          nodes.append(i)
          nodeIndexes.append(i[1])
          gScores.append(tentGScore)
          fScores.append(self.AstarHeur(finnish, i[1], tentGScore))
          fromList.append(current)
          opList.append(nodeIndex)
    
    return []

  
  def findKeyPressSequence(self, piece: int, placing: tuple[int, int, int], board: npt.NDArray[np.uint8]):
    fromList = self.AStar(piece, placing, board)

    print(fromList, file=log)

    moves = []
    if(len(fromList) > 0):
      moves.append(fromList[len(fromList) - 1][0])
      nodeIndex = fromList[len(fromList) - 1][3] - 1
      while(nodeIndex > 0):
        node = fromList[nodeIndex]
        moves.append(node[0])
        nodeIndex = node[3] - 1
      moves.append(fromList[0][0])
    
    return moves


    


  def compute(self, board: npt.NDArray[np.uint8]):
    
    piece = self.getShape(board)
    if(piece < 0):
      return []

    places = self.findPlaceAbleSpaces(board, piece)
    if(len(places) < 1):
      return []

    return self.findKeyPressSequence(piece, places[0], board)


def npArrFromImage(image: Image.Image):
  rows = image.height
  columns = image.width

  boardArr = np.zeros((rows, columns), dtype=np.uint8)

  for y in range(rows):
    for x in range(columns):

      position = ( x , y )
      boardArr[y, x] = 1 if image.getpixel(position) > 20 else 0
  
  return boardArr


# boardColumns = 10
# boardRows = 22

# im = Image.open("img/out8.png")

# boardArr = npArrFromImage(im)

# agente = AgenteTetris()

# print(boardArr)
# print('\n/----------------------------------------------/\n')
# # print(pieces[agente.getShape(boardArr)][0][0],pieces[agente.getShape(boardArr)][0][1],pieces[agente.getShape(boardArr)][0][2],pieces[agente.getShape(boardArr)][0][3],sep="\n")
# print('\n/----------------------------------------------/\n')
# agente.compute(boardArr)
# print('\n/----------------------------------------------/\n')



# --------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------ScreenShoot code------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------

def getBoardArr(boardRows, boardColums, boardArr):
  im = ag.screenshot(region=region)
  im = ImageOps.grayscale(im)
  for y in range(boardRows):
    for x in range(boardColumns):

      position = ( int(offset + step * x) , int(offset + step * y) )
      boardArr[y, x] = 1 if im.getpixel(position) > 40 else 0


time.sleep(0.5);

ag.moveTo(647, 370)
ag.click()
ag.sleep(0.3)
ag.moveTo(641, 647)
ag.click()
ag.sleep(0.3)
ag.moveTo(1089, 351)
ag.click()

ag.sleep(8)

ag.moveTo(341, 384)

region = (628,275,110,242)

boardColumns = 10
boardRows = 22

offset = 5
step = 11

boardArr = np.zeros((boardRows, boardColumns), dtype=np.uint8)

mousePos = ag.position()
agente = AgenteTetris()

while(mousePos[0] < 1024):

  getBoardArr(boardRows, boardColumns, boardArr)

  ag.moveRel(0, 100)
  print("====================================================", file=log)
  moves = agente.compute(boardArr)
  ag.moveRel(0, -100)
  if(len(moves) > 0):
    presses = [movements[i] for i in moves]
    print(presses, file=log)
    for i in presses:
      ag.keyDown(i)
      ag.sleep(0.05)
      ag.keyUp(i)
      ag.sleep(0.015)


  # print(boardArr)
  mousePos = ag.position()