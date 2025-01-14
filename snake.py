import pygame
import time
import numpy as np
import random

pygame.init()

#To adjust the grey
factor1 = 100
factor2 = 150

RED1 = (255, 20, 20)
RED2 = (200, 50, 50)
GREEN1 = (20, 255, 20)
GREEN2 = (30, 200, 30)
BLUE = (50, 50, 230)
BLUE2 = (0, 122, 255)
DARK_BLUE = (0, 100, 200)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MULTIGREY = (1, 1, 1)

#Multiplies every component in tuple by scalar
GREY1 = tuple(factor1 * component for component in MULTIGREY)
GREY2 = tuple(factor2 * component for component in MULTIGREY)

class Snake:
    def __init__(self, initLen, initDir, speed):
        self.length = initLen
        self.direction = initDir #eg. (-1, 0) = LEFT
        self.prevDirection = self.direction
        self.speed = speed
        self.moveTime = time.time() #The time since snake last moved

    #Will initially render snake, and give it attributes like coords
    #Could probably be in __init__
    def state0(self, initLen, gridSize):
        y = round((gridSize[1] - 1) / 2)

        #Initialises coord list for clarity
        rows = initLen
        coords = []

        for i in range(rows):
            #For length of n, coords go from 0 to n - 1
            coords.append((gridSize[0] - initLen + i, y))
        
        self.coords = coords #Gives itself the coords attribute
    
    def render_snake(self, PPS, window):
        offset = PPS/5

        #Render snake
        for i in range(self.length):
            x = self.coords[i][0] * PPS
            y = self.coords[i][1] * PPS
            rct = (x, y, PPS, PPS)
            rct2 = (x + offset, y + offset, PPS - 2 * offset, PPS - 2 * offset)
            if i == 0:
                pygame.draw.rect(window, BLUE, rct)
            else:
                pygame.draw.rect(window, GREEN1, rct)
                pygame.draw.rect(window, GREEN2, rct2)

    def move(self):
        now = time.time()

        if now - self.moveTime >= 1/self.speed: #Since speed is squares per second
            #Ensures 180 degree turn isnt possible
            if tuple(-1 * component for component in self.direction) != self.prevDirection:
                self.prevDirection = self.direction
            else:
                self.direction = self.prevDirection #Should cancel the 180 turn if attempted

            self.tail = self.coords[self.length - 1] #Need to save the last coordinates of tail in case snake grows

            for i in range(self.length - 1):
                #Makes count decending rather than accending
                j = self.length - 1 - i
                self.coords[j] = self.coords[j - 1]

            #Shit code but idk how to add a tuple to a list
            one = int(self.coords[0][0]) + self.direction[0]
            two = int(self.coords[0][1]) + self.direction[1]
            self.coords[0] = (one, two)
            self.moveTime = time.time()
    
    def grow(self):
        self.length += 1
        self.coords.append(self.tail)
    
    def check_fail(self, gridSize):
        #Check if snake is out of bounds
        x = self.coords[0][0]
        y = self.coords[0][1]
        if x < 0 or x > gridSize[0] - 1 or y < 0 or y > gridSize[1] - 1:
            return True

        #Could be more efficient by not checking element 1, 2, 3 since impossible to collide
        for i in range(self.length - 1):
            if self.coords[0] == self.coords[i + 1]:
                return True
        return False

class Apple:
    def __init__(self, gridSize):
        #Creates list of tuples
        rows = gridSize[0]
        cols = gridSize[1]

        self.totalSet = []
        for i in range(rows):
            for j in range(cols):
                self.totalSet.append((i, j))

    def state0(self, gridSize):
        y = round((gridSize[1] - 1) / 2)
        x = 2

        self.coords = (x, y)
    
    def render_apple(self, PPS, window):
        x = self.coords[0] * PPS
        y = self.coords[1] * PPS
        rct = (x, y, PPS, PPS)
        pygame.draw.rect(window, RED1, rct)

    def new_pos(self, snakeCoords, snakeLen):
        possibleSet = self.totalSet.copy() #Without the copy, the two variables share the same pointer, and so modify the same variable (i think)

        for i in range(snakeLen):
            if snakeCoords[i] in possibleSet:
                possibleSet.remove(snakeCoords[i])
        self.coords = random.choice(possibleSet)

            

def init_window(width, height, caption):
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption(caption)

    return window

def fail_screen(font, width, height, window, previousClick):
    window.fill(RED2)
    textSurface = font.render("Game Over!", True, WHITE)
    textRect = textSurface.get_rect(center=(width/2, height/2))
    retryButton = (width/2 - 100, height*3/5, 200, 50)
    previousClick, click = create_button(retryButton, DARK_BLUE, BLUE2, "Retry", font, window, previousClick)
    window.blit(textSurface, textRect)
    return previousClick, click

def render_grid(gridSize, PPS, window):
    #Remember y starts form the top

    #Effictively does half the squares
    window.fill(GREY1)

    #Draws other half of squares
    for j in range(gridSize[1]): #y coords
        for i in range(gridSize[0]): #x coords

            #Will alternate odd and even depending on row and column
            checkerNum = i + j

            #Draw on odd, not on even
            if checkerNum == 0 or checkerNum % 2 == 0:
                rct = (PPS*i, PPS*j, PPS, PPS)
                pygame.draw.rect(window, GREY2, rct)

def eat(snakeHead, apple):
    if snakeHead == apple:
        return True
    else:
        return False

def render_score(score, font, window):
    textSurface = font.render("Score: " + str(score), True, WHITE)
    textRect = textSurface.get_rect(center=(60, 40))
    window.blit(textSurface, textRect)

#Code taken from 'Open Me Flaps'
def create_button(rect, activeColour, passiveColour, text, font, window, previousClick): #Creates and handles button, rect = (x, y, width, height)
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    click = click[0]

    if rect[0] <= mouse[0] <= rect[0] + rect[2] and rect[1] <= mouse[1] <= rect[1] + rect[3]:
        pygame.draw.rect(window, activeColour, rect)
        if click == 1 and previousClick == 0:
            previousClick = click
            return previousClick, 1
    else:
        pygame.draw.rect(window, passiveColour, rect)
    
    #draw text on button
    textSurface = font.render(text, True, WHITE)
    textRect = textSurface.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3]//2))
    window.blit(textSurface, textRect)
    
    previousClick = click
    return previousClick, 0

def main():
    gridSize = [20, 15] #Grid size of snake board, doesnt have to be square, at least 3x3
    PPS = 50 #Pixels per square
    width = gridSize[0] * PPS
    height = gridSize[1] * PPS
    caption = "Snake!"

    initLen = 3 #Initial snake length
    initDir = (-1, 0) #Initial snake direction
    speed = 8 #Squares per second
    score = 0

    window = init_window(width, height, caption)
    font = pygame.font.Font(None, 36)  #None is defult font, number is size
    previousClick = 0

    snake = Snake(initLen, initDir, speed)
    snake.state0(initLen, gridSize)

    apple = Apple(gridSize)
    apple.state0(gridSize)

    playing = True
    scene = 0 #Which scene is currently being displayed

    displayGameOver = True #Whether there is a game over screen or if it just closes
    while playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    snake.direction = (1, 0)
                elif event.key == pygame.K_DOWN:
                    snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT:
                    snake.direction = (-1, 0)
                elif event.key == pygame.K_UP:
                    snake.direction = (0, -1)
        if scene == 0:
            render_grid(gridSize, PPS, window)
            snake.move()

            fail = snake.check_fail(gridSize)
            if fail == True:
                scene = 1
                if displayGameOver == False:
                    playing = False

            if eat(snake.coords[0], apple.coords) == True:
                snake.grow()
                apple.new_pos(snake.coords, snake.length)
                score += 1
            snake.render_snake(PPS, window)
            apple.render_apple(PPS, window)
            render_score(score, font, window)
        elif scene == 1:
            previousClick, click = fail_screen(font, width, height, window, previousClick)
            if click == 1:
                playing = False
                return True
        pygame.display.update()

#This exists because after a restart occurs, main needs to be run again, not just the bit looped in main
running = True
while running == True:
    running = main()