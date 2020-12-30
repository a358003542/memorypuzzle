#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import random
import sys
import pygame
import pygame_menu
import logging

from pygame.locals import *

logger = logging.getLogger(__name__)

from config import FPS, WINDOWWIDTH, WINDOWHEIGHT, REVEALSPEED, COVERSPEED, \
    BOXSIZE, GAPSIZE, BOARDWIDTH, BOARDHEIGHT, BGCOLOR, \
    LIGHTBGCOLOR, BOXCOLOR, HIGHLIGHTCOLOR, ICONS_NUMBER, DIFFICULTY, \
    MSYH_FONT_NAME, CATEGORY


def set_difficulty(value, difficulty):
    global DIFFICULTY
    DIFFICULTY = difficulty

    global ICONS_NUMBER
    global BOARDWIDTH
    global BOARDHEIGHT

    if DIFFICULTY == 'supereasy':
        ICONS_NUMBER = 4
        BOARDWIDTH = 6
        BOARDHEIGHT = 5
    elif DIFFICULTY == 'easy':
        ICONS_NUMBER = 6
        BOARDWIDTH = 8
        BOARDHEIGHT = 6
    elif DIFFICULTY == 'normal':
        ICONS_NUMBER = 8
        BOARDWIDTH = 10
        BOARDHEIGHT = 7
    elif DIFFICULTY == 'hard':
        ICONS_NUMBER = 10
        BOARDWIDTH = 10
        BOARDHEIGHT = 7
    elif DIFFICULTY == 'superhard':
        ICONS_NUMBER = 12
        BOARDWIDTH = 10
        BOARDHEIGHT = 7


def set_category(value, category):
    global CATEGORY
    CATEGORY = category


def try_load_msyh_font():
    """
    试着从windows系统加载微软雅黑字体
    :return:
    """
    pygame.font.init()
    try:
        msyh_font = pygame.font.Font("C:\Windows\Fonts\msyh.ttc", 24)
        for font_name in pygame.font.get_fonts():
            if os.path.samefile(pygame.font.match_font(font_name),
                                "C:\Windows\Fonts\msyh.ttc"):
                return font_name
    except FileNotFoundError as e:
        logger.error(f'微软雅黑字体没有找到')


def calc_xmargin():
    global WINDOWWIDTH
    global BOARDWIDTH
    global BOXSIZE
    global GAPSIZE
    return int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)


def calc_ymargin():
    global WINDOWHEIGHT
    global BOARDHEIGHT
    global BOXSIZE
    global GAPSIZE
    return int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)


def getRandomizedBoard():
    import glob
    filename_list = [os.path.basename(file) for file in
                     glob.glob(f'resource/{CATEGORY}/*.png')]
    icon_name_list = [os.path.splitext(filename)[0] for filename in
                      filename_list]
    icons = random.sample(icon_name_list, ICONS_NUMBER)

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


def drawIcon(icon_name, boxx, boxy):
    global CATEGORY
    left, top = leftTopCoordsOfBox(boxx,
                                   boxy)  # get pixel coords from board coords
    # Draw the icon
    iconImg = pygame.image.load(f'resource/{CATEGORY}/{icon_name}.png')
    iconImg = pygame.transform.scale(iconImg, (BOXSIZE, BOXSIZE))

    surface.blit(iconImg, (left, top))


def drawBoard(board, revealed):
    # Draws all of the boxes in their covered or revealed state.
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                # Draw a covered box.
                pygame.draw.rect(surface, BOXCOLOR,
                                 (left, top, BOXSIZE, BOXSIZE))
            else:
                # Draw the (revealed) icon.
                icon_name = getIconName(board, boxx, boxy)
                drawIcon(icon_name, boxx, boxy)


def splitIntoGroupsOf(groupSize, theList):
    # splits a list into a list of lists, where the inner lists have at
    # most groupSize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result


def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates

    left = boxx * (BOXSIZE + GAPSIZE) + calc_xmargin()
    top = boxy * (BOXSIZE + GAPSIZE) + calc_ymargin()
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
    global surface, clock
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(surface, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        icon_name = getIconName(board, box[0], box[1])
        drawIcon(icon_name, box[0], box[1])
        if coverage > 0:  # only draw the cover if there is an coverage
            pygame.draw.rect(surface, BOXCOLOR,
                             (left, top, coverage, BOXSIZE))
    pygame.display.update()
    clock.tick(FPS)


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
    pygame.draw.rect(surface, HIGHLIGHTCOLOR,
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
        surface.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)


def hasWon(revealedBoxes):
    # Returns True if all the boxes have been revealed, otherwise False
    for i in revealedBoxes:
        if False in i:
            return False  # return False if any boxes are covered.
    return True


def handle_game_event(mousex, mousey, mouseClicked):
    global firstSelection

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
                    revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                    revealedBoxes[boxx][boxy] = False

                elif hasWon(revealedBoxes):  # check if all pairs found
                    gameWonAnimation(mainBoard)

                firstSelection = None  # reset firstSelection variable


def resume_game():
    global main_menu
    global clock
    global mainBoard
    global revealedBoxes
    global firstSelection
    global pause_menu

    mousex = 0  # used to store x coordinate of mouse event
    mousey = 0  # used to store y coordinate of mouse event

    # Reset main menu and disable
    # You also can set another menu, like a 'pause menu', or just use the same
    # main_menu as the menu that will check all your input.
    main_menu.disable()
    main_menu.reset(1)

    while True:
        mouseClicked = False
        surface.fill(BGCOLOR)  # drawing the window
        drawBoard(mainBoard, revealedBoxes)

        # Application events
        events = pygame.event.get()

        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pause_menu.enable()  # process to the menu
                    return
            elif e.type == MOUSEMOTION:
                mousex, mousey = e.pos
            elif e.type == MOUSEBUTTONUP:
                mousex, mousey = e.pos
                mouseClicked = True

        # Continue playing
        handle_game_event(mousex, mousey, mouseClicked)
        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        clock.tick(FPS)


def start_game():
    global main_menu
    global clock
    global mainBoard
    global revealedBoxes
    global firstSelection

    # Reset main menu and disable
    # You also can set another menu, like a 'pause menu', or just use the same
    # main_menu as the menu that will check all your input.
    main_menu.disable()
    main_menu.reset(1)

    mousex = 0  # used to store x coordinate of mouse event
    mousey = 0  # used to store y coordinate of mouse event

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None  # stores the (x, y) of the first box clicked.

    surface.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    while True:
        # Application events
        mouseClicked = False
        surface.fill(BGCOLOR)  # drawing the window
        drawBoard(mainBoard, revealedBoxes)

        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pause_menu.enable()  # process to the menu
                    return
            elif e.type == MOUSEMOTION:
                mousex, mousey = e.pos
            elif e.type == MOUSEBUTTONDOWN:
                # left click
                if pygame.mouse.get_pressed()[0]:
                    mousex, mousey = e.pos
                    mouseClicked = True

        # Continue playing
        handle_game_event(mousex, mousey, mouseClicked)
        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        clock.tick(FPS)


def menu_background():
    """
    Function used by menus, draw on background while menu is active.
    :return: None
    """
    global surface
    surface.fill((128, 0, 128))


def return_titlepage():
    global main_menu
    pause_menu.disable()
    main_menu.enable()


def create_pause_menu():
    global pause_menu
    pause_menu = pygame_menu.Menu(WINDOWHEIGHT * 0.9, WINDOWWIDTH * 0.6,
                                  '欢迎',
                                  theme=MY_THEME_BLUE)

    pause_menu.add_button('继续游戏', resume_game)
    pause_menu.add_button('返回标题', return_titlepage)
    pause_menu.add_button('退出游戏', pygame_menu.events.EXIT)

    pause_menu.center_content()
    return pause_menu


def create_main_menu():
    global main_menu
    main_menu = pygame_menu.Menu(WINDOWHEIGHT * 0.9, WINDOWWIDTH * 0.6,
                                 '欢迎',
                                 theme=MY_THEME_BLUE)

    main_menu.add_selector('选择难度：',
                           [('超级简单', 'supereasy'), ('简单', 'easy'), \
                            ('普通', 'normal'), ('困难', 'hard'),
                            ('非常困难', 'superhard')],
                           onchange=set_difficulty,
                           )
    main_menu.add_selector('选择分类：',
                           [('水果', 'fruity'), ('体育', 'sports'),
                            ('糕点', 'bakery')],
                           onchange=set_category)

    main_menu.add_button('开始游玩', start_game)
    main_menu.add_button('退出游戏', pygame_menu.events.EXIT)

    main_menu.center_content()
    return main_menu


def main():
    global clock
    global main_menu
    global surface
    global MSYH_FONT_NAME
    global MY_THEME_BLUE
    pygame.init()

    MSYH_FONT_NAME = try_load_msyh_font()

    MY_THEME_BLUE = pygame_menu.themes.THEME_BLUE.copy()
    MY_THEME_BLUE.title_font = MSYH_FONT_NAME
    MY_THEME_BLUE.widget_font = MSYH_FONT_NAME

    surface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Memory Puzzle Game')

    clock = pygame.time.Clock()

    main_menu = create_main_menu()
    pause_menu = create_pause_menu()
    pause_menu.disable()

    while True:
        # handle menu event
        main_menu.mainloop(surface, menu_background, fps_limit=FPS)
        pause_menu.mainloop(surface, menu_background, fps_limit=FPS)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
