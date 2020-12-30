#!/usr/bin/env python
# -*-coding:utf-8-*-

import pygame

FPS = 60  # frames per second, the general speed of the program
DIFFICULTY = 'supereasy'
CATEGORY = 'fruity'
ICONS_NUMBER = 4
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

MSYH_FONT_NAME = 'microsoftyaheimicrosoftyaheiui'


assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, \
    'Board needs to have an even number of boxes for pairs of matches.'

