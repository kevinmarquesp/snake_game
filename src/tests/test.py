#!/usr/bin/env python

import curses


def teste(screen):
    curses.curs_set(False)
    screen.clear()

    while 1:

        key = screen.getch()
        screen.addstr(5, 5, f"Tecla precionada: {key}")
        screen.refresh()


curses.wrapper(teste)
