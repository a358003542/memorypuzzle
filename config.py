#!/usr/bin/env python
# -*-coding:utf-8-*-

import pygame
import os
import logging

logger = logging.getLogger(__name__)

FPS = 60  # frames per second, the general speed of the program
DIFFICULTY = 'supereasy'
CATEGORY = 'fruity'
ICONS_NUMBER = 2
WINDOWWIDTH = 640  # size of window's width in pixels
WINDOWHEIGHT = 490  # size of windows' height in pixels
BOARDWIDTH = 6  # number of columns of icons
BOARDHEIGHT = 5  # number of rows of icons

REVEALSPEED = 8  # speed boxes' sliding reveals and covers
COVERSPEED = 300  # 300ms then cover it
BOXSIZE = 48  # size of box height & width in pixels
GAPSIZE = 10  # size of gap between boxes in pixels

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
BLUE = pygame.Color('blue')
GRAY = pygame.Color('gray')
NAVYBLUE = pygame.Color('navyblue')
BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

# MSYH_FONT_NAME = 'microsoftyaheimicrosoftyaheiui'

assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, \
    'Board needs to have an even number of boxes for pairs of matches.'


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

MSYH_FONT_NAME = try_load_msyh_font()

