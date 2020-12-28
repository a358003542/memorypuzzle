#!/usr/bin/env python
# -*-coding:utf-8-*-

import pygame

FPS = 60  # frames per second, the general speed of the program
DIFFICULTY = 'supereasy'
ICONS_NUMBER = 4
WINDOWWIDTH = 384  # size of window's width in pixels
WINDOWHEIGHT = 350  # size of windows' height in pixels
BOARDWIDTH = 6  # number of columns of icons
BOARDHEIGHT = 5  # number of rows of icons

REVEALSPEED = 8  # speed boxes' sliding reveals and covers
COVERSPEED = 300  # 300ms then cover it
BOXSIZE = 48  # size of box height & width in pixels
GAPSIZE = 10  # size of gap between boxes in pixels

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


ALL_FRUIT = ['apple', 'banana', 'cherry', 'grape', 'kiwi_fruit', 'lemon',
             'mango', 'mangosteen', 'orange', 'pear', 'strawberry',
             'watermelon']


assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, \
    'Board needs to have an even number of boxes for pairs of matches.'
