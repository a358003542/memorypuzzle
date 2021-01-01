#!/usr/bin/env python
# -*-coding:utf-8-*-

import glob
import os
import random
import sys
import pygame
import pygame_menu
import logging
from dataclasses import dataclass

from pygame.locals import *

import config

logger = logging.getLogger(__name__)


@dataclass
class GameStatus:
    """
    一局游戏的核心状态 可以根据这个参量随时复原游戏
    """
    mainBoard: list
    revealedBoxes: list
    firstSelection: tuple = ()
    game_end: bool = False

    def get_icon_name(self, boxx, boxy):
        return self.mainBoard[boxx][boxy]

    def draw_board(self):
        for boxx in range(config.BOARDWIDTH):
            for boxy in range(config.BOARDHEIGHT):
                left, top = get_box_leftTopCoords(boxx, boxy)
                if not self.revealedBoxes[boxx][boxy]:
                    # Draw a covered box.
                    pygame.draw.rect(surface, config.BOXCOLOR,
                                     (left, top, config.BOXSIZE,
                                      config.BOXSIZE))
                else:
                    # Draw the (revealed) icon.
                    icon_name = self.get_icon_name(boxx, boxy)
                    draw_icon(icon_name, boxx, boxy)

    def start_game_animation(self):
        boxes = []
        for x in range(config.BOARDWIDTH):
            for y in range(config.BOARDHEIGHT):
                boxes.append((x, y))
        random.shuffle(boxes)

        def split_into_groups_of(groupSize, theList):
            # splits a list into a list of lists, where the inner lists have at
            # most groupSize number of items.
            result = []
            for i in range(0, len(theList), groupSize):
                result.append(theList[i:i + groupSize])
            return result

        boxGroups = split_into_groups_of(8, boxes)

        game_status.draw_board()

        for boxGroup in boxGroups:
            self.reveal_boxes_animation(boxGroup)
            self.cover_boxes_animation(boxGroup)

    def reveal_boxes_animation(self, boxesToReveal):
        # Do the "box reveal" animation.
        for coverage in range(config.BOXSIZE, (-config.REVEALSPEED) - 1,
                              -config.REVEALSPEED):
            draw_box_covers(self.mainBoard, boxesToReveal, coverage)

    def cover_boxes_animation(self, boxesToCover):
        # Do the "box cover" animation.
        for coverage in range(0, config.BOXSIZE + config.REVEALSPEED,
                              config.REVEALSPEED):
            draw_box_covers(self.mainBoard, boxesToCover, coverage)

    def game_won_animation(self):
        color1 = config.LIGHTBGCOLOR
        color2 = config.BGCOLOR

        for i in range(13):
            color1, color2 = color2, color1  # swap colors
            surface.fill(color1)
            self.draw_board()
            pygame.display.update()
            pygame.time.wait(300)

    def has_won(self):
        # Returns True if all the boxes have been revealed, otherwise False
        for i in self.revealedBoxes:
            if False in i:
                return False  # return False if any boxes are covered.
        return True


def set_difficulty(value, difficulty):
    config.DIFFICULTY = difficulty

    if difficulty == 'supereasy':
        config.ICONS_NUMBER = 2
        config.BOARDWIDTH = 6
        config.BOARDHEIGHT = 5
    elif difficulty == 'easy':
        config.ICONS_NUMBER = 4
        config.BOARDWIDTH = 8
        config.BOARDHEIGHT = 6
    elif difficulty == 'normal':
        config.ICONS_NUMBER = 6
        config.BOARDWIDTH = 10
        config.BOARDHEIGHT = 7
    elif difficulty == 'hard':
        config.ICONS_NUMBER = 8
        config.BOARDWIDTH = 10
        config.BOARDHEIGHT = 7
    elif difficulty == 'superhard':
        config.ICONS_NUMBER = 10
        config.BOARDWIDTH = 10
        config.BOARDHEIGHT = 7


def set_category(value, category):
    config.CATEGORY = category


def calc_xmargin():
    return int((config.WINDOWWIDTH -
                (config.BOARDWIDTH * (config.BOXSIZE +
                                      config.GAPSIZE))) / 2)


def calc_ymargin():
    return int((config.WINDOWHEIGHT -
                (config.BOARDHEIGHT * (config.BOXSIZE +
                                       config.GAPSIZE))) / 2)


def gen_random_board():
    filename_list = [os.path.basename(file) for file in
                     glob.glob(f'resource/{config.CATEGORY}/*.png')]
    icon_name_list = [os.path.splitext(filename)[0] for filename in
                      filename_list]
    icons = random.sample(icon_name_list, config.ICONS_NUMBER)

    # calculate how many icons are needed
    numIconsUsed = int(config.BOARDWIDTH * config.BOARDHEIGHT / 2)

    while numIconsUsed > len(icons):
        icons.append(random.choice(icons))

    icons = icons[:numIconsUsed] * 2
    random.shuffle(icons)

    # Create the board data structure, with randomly placed icons.
    board = []
    index = 0
    for x in range(config.BOARDWIDTH):
        column = []
        for y in range(config.BOARDHEIGHT):
            column.append(icons[index])
            index += 1
        board.append(column)
    return board


def gen_revealed_boxes():
    revealedBoxes = []
    for i in range(config.BOARDWIDTH):
        revealedBoxes.append([False] * config.BOARDHEIGHT)
    return revealedBoxes


def draw_icon(icon_name, boxx, boxy):
    left, top = get_box_leftTopCoords(boxx,
                                      boxy)
    # Draw the icon
    iconImg = pygame.image.load(
        f'resource/{config.CATEGORY}/{icon_name}.png')
    iconImg = pygame.transform.scale(iconImg, (
        config.BOXSIZE, config.BOXSIZE))

    surface.blit(iconImg, (left, top))


def get_box_leftTopCoords(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (
            config.BOXSIZE + config.GAPSIZE) + calc_xmargin()
    top = boxy * (
            config.BOXSIZE + config.GAPSIZE) + calc_ymargin()
    return (left, top)


def get_box_at_pixel(x, y):
    for boxx in range(config.BOARDWIDTH):
        for boxy in range(config.BOARDHEIGHT):
            left, top = get_box_leftTopCoords(boxx, boxy)
            boxRect = pygame.Rect(left, top, config.BOXSIZE,
                                  config.BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


def draw_box_covers(board, boxes, coverage):
    # Draws boxes being covered/revealed. "boxes" is a list
    # of two-item lists, which have the x & y spot of the box.
    global surface, clock
    for box in boxes:
        left, top = get_box_leftTopCoords(box[0], box[1])
        pygame.draw.rect(surface, config.BGCOLOR, (
            left, top, config.BOXSIZE, config.BOXSIZE))
        icon_name = game_status.get_icon_name(box[0], box[1])
        draw_icon(icon_name, box[0], box[1])
        if coverage > 0:  # only draw the cover if there is an coverage
            pygame.draw.rect(surface, config.BOXCOLOR,
                             (left, top, coverage, config.BOXSIZE))
    pygame.display.update()
    clock.tick(config.FPS)


def draw_highlight_box(boxx, boxy):
    left, top = get_box_leftTopCoords(boxx, boxy)
    pygame.draw.rect(surface, config.HIGHLIGHTCOLOR,
                     (left - 5, top - 5, config.BOXSIZE + 10,
                      config.BOXSIZE + 10), 4)


def handle_game_event(mousex, mousey, mouseClicked):
    global game_status

    boxx, boxy = get_box_at_pixel(mousex, mousey)
    if boxx is not None and boxy is not None:
        # The mouse is currently over a box.
        if not game_status.revealedBoxes[boxx][boxy]:
            draw_highlight_box(boxx, boxy)
        if not game_status.revealedBoxes[boxx][boxy] and mouseClicked:
            game_status.reveal_boxes_animation([(boxx, boxy)])
            game_status.revealedBoxes[boxx][
                boxy] = True  # set the box as "revealed"
            if not game_status.firstSelection:
                game_status.firstSelection = (boxx, boxy)
            else:
                icon1shape = game_status.get_icon_name(
                    game_status.firstSelection[0],
                    game_status.firstSelection[1])
                icon2shape = game_status.get_icon_name(boxx,
                                                       boxy)

                if icon1shape != icon2shape:
                    # Icons don't match. Re-cover up both selections.
                    pygame.time.wait(config.COVERSPEED)
                    game_status.cover_boxes_animation([
                        (game_status.firstSelection[0],
                         game_status.firstSelection[1]),
                        (boxx, boxy)])
                    game_status.revealedBoxes[game_status.firstSelection[0]][
                        game_status.firstSelection[1]] = False
                    game_status.revealedBoxes[boxx][boxy] = False

                elif game_status.has_won():  # check if all pairs found
                    game_status.game_won_animation()
                    return_titlepage()
                    game_status.game_end = True

                game_status.firstSelection = ()  # reset firstSelection variable


def resume_game():
    mousex = 0  # used to store x coordinate of mouse event
    mousey = 0  # used to store y coordinate of mouse event

    main_menu.disable()
    main_menu.reset(1)

    while not game_status.game_end:
        mouseClicked = False
        surface.fill(config.BGCOLOR)  # drawing the window
        game_status.draw_board()

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
        clock.tick(config.FPS)


def start_game():
    global game_status

    main_menu.disable()
    main_menu.reset(1)

    mousex = 0  # used to store x coordinate of mouse event
    mousey = 0  # used to store y coordinate of mouse event

    game_status = GameStatus(mainBoard=gen_random_board(),
                             revealedBoxes=gen_revealed_boxes(),
                             )

    surface.fill(config.BGCOLOR)
    game_status.start_game_animation()

    while not game_status.game_end:
        # Application events
        mouseClicked = False
        surface.fill(config.BGCOLOR)  # drawing the window
        game_status.draw_board()

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
        clock.tick(config.FPS)


def menu_background():
    """
    Function used by menus, draw on background while menu is active.
    :return: None
    """
    surface.fill((128, 0, 128))


def return_titlepage():
    pause_menu.disable()
    main_menu.enable()


def create_pause_menu(theme):
    pause_menu = pygame_menu.Menu(config.WINDOWHEIGHT * 0.9,
                                  config.WINDOWWIDTH * 0.6,
                                  '欢迎',
                                  theme=theme)

    pause_menu.add_button('继续游戏', resume_game)
    pause_menu.add_button('返回标题', return_titlepage)
    pause_menu.add_button('退出游戏', pygame_menu.events.EXIT)

    pause_menu.center_content()
    return pause_menu


def create_main_menu(theme):
    main_menu = pygame_menu.Menu(config.WINDOWHEIGHT * 0.9,
                                 config.WINDOWWIDTH * 0.6,
                                 '欢迎',
                                 theme=theme)

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
    global pause_menu
    global surface

    pygame.init()

    MY_THEME_BLUE = pygame_menu.themes.THEME_BLUE.copy()
    MY_THEME_BLUE.title_font = config.MSYH_FONT_NAME
    MY_THEME_BLUE.widget_font = config.MSYH_FONT_NAME

    surface = pygame.display.set_mode((config.WINDOWWIDTH, config.WINDOWHEIGHT))
    pygame.display.set_caption('Memory Puzzle Game')

    clock = pygame.time.Clock()

    main_menu = create_main_menu(MY_THEME_BLUE)
    pause_menu = create_pause_menu(MY_THEME_BLUE)
    pause_menu.disable()

    while True:
        # handle menu event
        main_menu.mainloop(surface, menu_background, fps_limit=config.FPS)
        pause_menu.mainloop(surface, menu_background, fps_limit=config.FPS)

        pygame.display.update()
        clock.tick(config.FPS)


if __name__ == '__main__':
    main()
