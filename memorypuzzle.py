#!/usr/bin/env python
# -*-coding:utf-8-*-

import random
import sys
import pygame
import pygame_menu

from pygame.locals import *

FPS = 60  # frames per second, the general speed of the program
WINDOWWIDTH = 640  # size of window's width in pixels
WINDOWHEIGHT = 480  # size of windows' height in pixels
REVEALSPEED = 8  # speed boxes' sliding reveals and covers
COVERSPEED = 300  # 300ms then cover it
BOXSIZE = 48  # size of box height & width in pixels
GAPSIZE = 10  # size of gap between boxes in pixels
BOARDWIDTH = 10  # number of columns of icons
BOARDHEIGHT = 7  # number of rows of icons

assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, \
    'Board needs to have an even number of boxes for pairs of matches.'

XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
BLUE = pygame.Color('blue')
GRAY = pygame.Color('gray')
NAVYBLUE = pygame.Color('navyblue')

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

DIFFICULTY = 'supereasy'
fruit_number = 4
BOARDWIDTH = 6
BOARDHEIGHT = 5


def set_difficulty(value, difficulty):
    DIFFICULTY = value[0]
    global fruit_number
    global BOARDWIDTH
    global BOARDHEIGHT
    if DIFFICULTY == 'supereasy':
        fruit_number = 4
        BOARDWIDTH = 6
        BOARDHEIGHT = 5
    elif DIFFICULTY == 'easy':
        fruit_number = 6
        BOARDWIDTH = 8
        BOARDHEIGHT = 6
    elif DIFFICULTY == 'normal':
        fruit_number = 8
        BOARDWIDTH = 10
        BOARDHEIGHT = 7
    elif DIFFICULTY == 'hard':
        fruit_number = 10
        BOARDWIDTH = 10
        BOARDHEIGHT = 7
    elif DIFFICULTY == 'superhard':
        fruit_number = 12
        BOARDWIDTH = 10
        BOARDHEIGHT = 7

    print(fruit_number, BOARDHEIGHT, BOARDWIDTH)


ALL_FRUIT = ['apple', 'banana', 'cherry', 'grape', 'kiwi_fruit', 'lemon',
             'mango', 'mangosteen', 'orange', 'pear', 'strawberry',
             'watermelon']


def getRandomizedBoard():
    icons = random.sample(ALL_FRUIT, fruit_number)

    # calculate how many icons are needed
    numIconsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2)

    while numIconsUsed > len(icons):
        icons.append(random.choice(icons))

    icons = icons[:numIconsUsed] * 2
    random.shuffle(icons)

    # Create the board data structure, with randomly placed icons.
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            del icons[0]  # remove the icons as we assign them
        board.append(column)
    return board


def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val] * BOARDHEIGHT)
    return revealedBoxes


def getIconName(board, boxx, boxy):
    # shape value for x, y spot is stored in board[x][y][0]
    # color value for x, y spot is stored in board[x][y][1]
    return board[boxx][boxy]


def drawIcon(shape, boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx,
                                   boxy)  # get pixel coords from board coords
    # Draw the icon
    iconImg = pygame.image.load(f'resource/fruity/{shape}.png')
    iconImg = pygame.transform.scale(iconImg, (BOXSIZE, BOXSIZE))

    DISPLAYSURF.blit(iconImg, (left, top))


def drawBoard(board, revealed):
    # Draws all of the boxes in their covered or revealed state.
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                # Draw a covered box.
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR,
                                 (left, top, BOXSIZE, BOXSIZE))
            else:
                # Draw the (revealed) icon.
                shape = getIconName(board, boxx, boxy)
                drawIcon(shape, boxx, boxy)


def start_game():
    global FPSCLOCK, DISPLAYSURF

    FPSCLOCK = pygame.time.Clock()

    mousex = 0  # used to store x coordinate of mouse event
    mousey = 0  # used to store y coordinate of mouse event
    pygame.display.set_caption('Memory Game')

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None  # stores the (x, y) of the first box clicked.

    DISPLAYSURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    while True:  # main game loop
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR)  # drawing the window
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                menu.mainloop(DISPLAYSURF)
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            # The mouse is currently over a box.
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True  # set the box as "revealed"
                if firstSelection == None:  # the current box was the first box clicked
                    firstSelection = (boxx, boxy)
                else:  # the current box was the second box clicked
                    # Check if there is a match between the two icons.
                    icon1shape = getIconName(mainBoard,
                                             firstSelection[0],
                                             firstSelection[1])
                    icon2shape = getIconName(mainBoard, boxx,
                                             boxy)

                    if icon1shape != icon2shape:
                        # Icons don't match. Re-cover up both selections.
                        pygame.time.wait(COVERSPEED)
                        coverBoxesAnimation(mainBoard, [
                            (firstSelection[0], firstSelection[1]),
                            (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][
                            firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False

                    elif hasWon(revealedBoxes):  # check if all pairs found
                        gameWonAnimation(mainBoard)
                        menu.mainloop(DISPLAYSURF)

                    firstSelection = None  # reset firstSelection variable

        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def splitIntoGroupsOf(groupSize, theList):
    # splits a list into a list of lists, where the inner lists have at
    # most groupSize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result


def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)


def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


def drawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed. "boxes" is a list
    # of two-item lists, which have the x & y spot of the box.
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        shape = getIconName(board, box[0], box[1])
        drawIcon(shape, box[0], box[1])
        if coverage > 0:  # only draw the cover if there is an coverage
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR,
                             (left, top, coverage, BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def revealBoxesAnimation(board, boxesToReveal):
    # Do the "box reveal" animation.
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    # Do the "box cover" animation.
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR,
                     (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)


def startGameAnimation(board):
    # Randomly reveal the boxes 8 at a time.
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append((x, y))
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)


def gameWonAnimation(board):
    # flash the background color when the player has won
    coveredBoxes = generateRevealedBoxesData(True)
    color1 = LIGHTBGCOLOR
    color2 = BGCOLOR

    for i in range(13):
        color1, color2 = color2, color1  # swap colors
        DISPLAYSURF.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)


def hasWon(revealedBoxes):
    # Returns True if all the boxes have been revealed, otherwise False
    for i in revealedBoxes:
        if False in i:
            return False  # return False if any boxes are covered.
    return True


DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.init()

menu = pygame_menu.Menu(300, 400, 'Welcome',
                        theme=pygame_menu.themes.THEME_BLUE)


def main():
    menu.add_selector('Difficulty :',
                      [('supereasy', 1), ('easy', 2), ('normal', 3),
                       ('hard', 4), ('superhard', 5)],
                      onchange=set_difficulty)
    menu.add_button('Play', start_game)
    menu.add_button('Quit', pygame_menu.events.EXIT)
    menu.add_button('Close Menu', pygame_menu.events.CLOSE)
    menu.mainloop(DISPLAYSURF)


if __name__ == '__main__':
    main()
