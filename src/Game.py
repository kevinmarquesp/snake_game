import curses


def drawn_box(stdsrc, start, end):
    stdsrc.addstr(start[0], start[1], "┌")
    stdsrc.addstr(start[0], end[1],   "┐")
    stdsrc.addstr(end[0],   start[1], "└")
    stdsrc.addstr(end[0],   end[1],   "┘")

    # Drawning horizontal lines
    for i in range(start[1] + 1, end[1]):
        stdsrc.addstr(start[0], i, "─")
        stdsrc.addstr(end[0],   i, "─")

    # Drawning vertical lines
    for i in range(start[0] + 1, end[0]):
        stdsrc.addstr(i, start[1], "│")
        stdsrc.addstr(i, end[1],   "│")

    stdsrc.refresh()


class MenuUI:
    def __init__(self):
        self.selected_item = 0 # Save the selected row
        self.menu_items = ["Play", "Scoreboard", "EXIT"]

        curses.wrapper(self.start_menu)


    def start_menu(self, stdsrc):
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)

        while 1:
            stdsrc.clear()
            self.y_len, self.x_len = stdsrc.getmaxyx()

            drawn_box(stdsrc, [5, 14], [self.y_len - 6, self.x_len - 15])

            self.show_menu(stdsrc)
            key = stdsrc.getch()


            # "J" pressed
            if key == 107 and self.selected_item > 0:
                self.selected_item -= 1

            # "F" pressed
            elif key == 106 and self.selected_item < len(self.menu_items) - 1:
                self.selected_item += 1

            # "Return" pressed
            elif key == curses.KEY_ENTER or key in [10, 13]:
                break


    def show_menu(self, stdsrc):
        for index, text in enumerate(self.menu_items):
            x = self.x_len // 2 - len(text) // 2
            y = self.y_len // 2 - len(self.menu_items) // 2 + index

            if self.selected_item == index:
                stdsrc.attron(curses.color_pair(1))

            stdsrc.addstr(y, x, text)
            stdsrc.attroff(curses.color_pair(1))

        stdsrc.refresh()
