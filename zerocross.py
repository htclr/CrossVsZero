"""
Игра Крестики - Нолики
"""
import arcade
from random import choice
from time import sleep

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Крестики - Нолики"
BACKGROUND_COLOR = (153, 102, 153)
LINES_COLOR = (0, 51, 102)
ZERO_COLOR = (0, 255, 153)
CROSS_COLOR = (204, 255, 51)
LINE_WIDTH = 8


class InstructionView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

    def on_draw(self):
        """ Draw this view """
        self.clear()
        arcade.draw_text("Кто ходит первым?", 300, 350,
                         arcade.color.WHITE, font_size=32, anchor_x="center")
        arcade.draw_text("Игрок - Нажми левую кнопку мыши", 300, 300,
                         arcade.color.WHITE, font_size=18, anchor_x="center")
        arcade.draw_text("Компьютер - Нажми правую", 300, 250,
                         arcade.color.WHITE, font_size=18, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        game_view = GameView()
        game_view.setup()
        if _button == arcade.MOUSE_BUTTON_RIGHT:
            game_view.save_move((300, 300))
        self.window.show_view(game_view)


class GameOverView(arcade.View):
    """ View to show when game is over """

    def __init__(self, winner):
        """ This is run once when we switch to this view """
        super().__init__()
        self.winner = winner

    def on_draw(self):
        """ Draw this view """

        def win_o():
            arcade.draw_text('Победа:', 300,
                             350, arcade.color.WHITE,
                             font_size=50, anchor_x="center")
            arcade.draw_circle_outline(300, 200, 90, ZERO_COLOR,
                                       LINE_WIDTH)

        def win_x():
            arcade.draw_text('Победа:', 300,
                             350, arcade.color.WHITE,
                             font_size=50, anchor_x="center")
            arcade.draw_line(230, 180, 370, 320,
                             CROSS_COLOR, LINE_WIDTH)
            arcade.draw_line(230, 320, 370, 180,
                             CROSS_COLOR, LINE_WIDTH)

        def win_n():
            arcade.draw_text('Ничья!', self.window.width / 2,
                             self.window.height / 2,
                             arcade.color.WHITE, font_size=60,
                             anchor_x="center")

        winner_list = {
            'o': win_o,
            'x': win_x,
            'n': win_n
        }

        self.clear()

        if self.winner in winner_list:
            winner_list[self.winner]()
        else:
            raise ValueError('Unknown winner')

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, re-start the game. """
        instruction_view = InstructionView()
        self.window.show_view(instruction_view)


class GameView(arcade.View):
    """
    Main application class.
    """

    cross_list = []
    zero_list = []
    last_x = False
    first_move = False
    make_move = False
    gameover = False

    def __init__(self):
        super().__init__()
        arcade.set_background_color(BACKGROUND_COLOR)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.cross_list = []
        self.zero_list = []
        self.gameover = False
        self.clear()

    def check_move(self, pos: tuple) -> bool:
        if pos in self.cross_list or pos in self.zero_list:
            return False
        return True

    def random_move(self):
        if (len(self.zero_list) + len(self.cross_list) >= 9):
            return None
        pos = (choice([100, 300, 500]), choice([100, 300, 500]))
        while not self.check_move(pos):
            pos = (choice([100, 300, 500]), choice([100, 300, 500]))
        return pos

    def human_move(self, pos) -> bool:
        def nc(n):
            if n <= 200:
                return 100
            if n <= 400:
                return 300
            if n <= 600:
                return 500
        x, y = pos
        np = (nc(x), nc(y))
        if self.check_move(np):
            return np
        return None

    def save_move(self, pos):
        if self.last_x:
            self.zero_list.append(pos)
        else:
            self.cross_list.append(pos)
        self.last_x = not self.last_x

    def check_win(self):
        if ((len(self.zero_list) + len(self.cross_list)) >= 9):
            return 'n'

        def check(move_list):
            xl = [c[0] for c in move_list]
            yl = [c[1] for c in move_list]
            for x in xl:
                if xl.count(x) == 3:
                    return True
            for y in yl:
                if yl.count(y) == 3:
                    return True
            diag_set1 = {(100, 100), (300, 300), (500, 500)}
            diag_set2 = {(100, 500), (300, 300), (500, 100)}
            move_set = set(move_list)
            if (diag_set1.issubset(set(move_set))
                    or diag_set2.issubset(set(move_set))):
                return True
            return False
        if check(self.cross_list):
            return 'x'
        if check(self.zero_list):
            return 'o'
        return None

    def on_draw(self):
        """Render the screen."""
        self.clear()

        def draw_0(x, y):
            arcade.draw_circle_outline(x, y, 90, ZERO_COLOR, LINE_WIDTH)

        def draw_x(x, y):
            OFFSET = 70
            arcade.draw_line(x - OFFSET, y - OFFSET, x + OFFSET, y + OFFSET,
                             CROSS_COLOR, LINE_WIDTH)
            arcade.draw_line(x - OFFSET, y + OFFSET, x + OFFSET, y - OFFSET,
                             CROSS_COLOR, LINE_WIDTH)

        for x in range(0, 600, 200):
            arcade.draw_line(x, 0, x, 600, LINES_COLOR, 4)
            arcade.draw_line(0, x, 600, x, LINES_COLOR, 4)

        for x, y in self.zero_list:
            draw_0(x, y)

        for x, y in self.cross_list:
            draw_x(x, y)

    def on_update(self, delta_time: float):
        win = self.check_win()
        if win:
            sleep(1)
            view = GameOverView(win)
            self.cross_list = []
            self.zero_list = []
            self.window.show_view(view)
            self.make_move = False
            return

        if self.make_move:
            self.make_move = False
            sleep(0.5)
            rm = self.random_move()
            if rm:
                self.save_move(rm)
                if win:
                    self.gameover = True
                    view = GameOverView(win)
                    self.window.show_view(view)

    def on_mouse_press(self, x, y, button, modifiers):
        pos = (x, y)
        hm = self.human_move(pos)
        if hm:
            self.save_move(hm)
            self.make_move = True


def main():
    """Main function"""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
