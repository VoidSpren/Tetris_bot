import pyautogui as ag
from PIL import Image, ImageOps
import numpy as np
import numpy.typing as npt
import time
import os

from tetrisPieces import pieces

movements = {"l": "left", "r": "rigth", "d":"down", "CW": "x", "CCW": "z", "drop": "space", "180": "A"}
inverted = {"l": "r", "r": "l", "u":"d", "CW": "CCW", "CCW": "CW", "undrp": "drop", "180": "180"}


class AgenteTetris:
  def __init__(self) -> None:
    self.rows = 20
    self.columns = 10
    self.minRow = 2
    self.savedPiece: int = None

  def getRow(self, row: int):
    return row + self.minRow
  
  def getShape(self, board: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    shape = np.zeros((2, 4), dtype=np.uint8)

    pieceIndex = -1

    for y in range(2):
      for x in range(4):
        shape[y, x] = board[y, x + 3] 
    
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
    
    if(pieceIndex < 0):
      RuntimeError(shape)

    return pieceIndex
  
  def checkCollision(self, x: int, y: int, r: int, piece: int, board: npt.NDArray[np.uint8]):
    for i in range(4):
      row = y + i

      for j in range(4):
        column = x + j

        if(pieces[piece][r][i][j] == 1 and
           (row >= self.rows or row < 0 or
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
  
  def findKeyPressSequence(self, piece: int, placing: tuple[int, int, int]):
    edges = inverted.keys()
    #TODO FINNISH


  def compute(self, board: npt.NDArray[np.uint8]):
    piece = self.getShape(board)
    places = self.findPlaceAbleSpaces(board, piece)
    self.findKeyPressSequence(piece, places[0])


def npArrFromImage(image: Image.Image):
  rows = image.height
  columns = image.width

  boardArr = np.zeros((rows, columns), dtype=np.uint8)

  for y in range(rows):
    for x in range(columns):

      position = ( x , y )
      boardArr[y, x] = 1 if image.getpixel(position) > 20 else 0
  
  return boardArr


boardColumns = 10
boardRows = 22

im = Image.open("img/out8.png")

boardArr = npArrFromImage(im)

agente = AgenteTetris()

print(boardArr)
print('\n/----------------------------------------------/\n')
print(pieces[agente.getShape(boardArr)][0][0],pieces[agente.getShape(boardArr)][0][1],pieces[agente.getShape(boardArr)][0][2],pieces[agente.getShape(boardArr)][0][3],sep="\n")
print('\n/----------------------------------------------/\n')
agente.compute(boardArr)
print('\n/----------------------------------------------/\n')



#--------------------------------------------------------------------------------------------------------------------------------
#----------------------------------ScreenShoot code------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------

# time.sleep(5);

# ag.moveTo(910, 370)
# ag.click()
# ag.sleep(0.2)
# ag.moveTo(902, 647)
# ag.click()
# ag.sleep(0.2)
# ag.moveTo(1531, 351)
# ag.click()

# ag.sleep(7.7)

# ag.moveTo(960, 540)


# region = (876, 359, 270, 370)

# im = ag.screenshot(region=region)
# im = ImageOps.grayscale(im)

# boardColumns = 10
# boardRows = 22

# offset = 8
# step = 16.85

# boardArr = np.zeros((boardRows, boardColumns), dtype=np.uint8)

# for i in range(10):

#   im = ag.screenshot(region=region)
#   im = ImageOps.grayscale(im)

#   for y in range(boardRows):
#     for x in range(boardColumns):

#       position = ( int(offset + step * x) , int(offset + step * y) )
#       boardArr[y, x] = 1 if im.getpixel(position) > 20 else 0

#   agente = AgenteTetris()

#   print(boardArr)
#   print('\n/----------------------------------------------/\n')

#   ag.press('space')

# ag.keyDown('esc')
# ag.sleep(3)
# ag.keyUp('esc')
