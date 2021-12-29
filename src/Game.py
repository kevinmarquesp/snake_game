from curses.textpad import rectangle
from datetime import datetime
import curses, random


class Globals:
    """
     *  GLOBALS: Aqui guarda a maiora das informações ecenciais para
     *  o jogo, mas elas podem ser acessadas pelas outras classes.
    """

    def __init__(self):
        self.keys = {
            "left":     [ 97, 104, 260],
            "down":     [115, 106, 258],
            "up":       [119, 107, 259],
            "right":    [100, 108, 261],
            "return":   [ 32, 111,  10]
        }
        self.oposite = {
            "right": "left",    "left": "right",
            "up": "down",        "down": "up"
        }

        self.menu_list = [
            "Play", "Scoreboard", "EXIT"
        ]

        self.directions_list = list()
        self.__gen_directions()


    # Essa função apenas constroe o self.directions_list automáticamente.
    def __gen_directions(self):
        all_directions = ["left", "down", "up", "right"]

        for directions_group in all_directions:
            for single_direction in directions_group:
                self.directions_list.append(single_direction)


class Menu(Globals):
    """
     *  MENU: Escreve as primeiras opções na tela, e guarda o valor do
     *  item selecionado em self.selected_item.
    """

    def __init__(self):
        super().__init__()

        # Guarda o index do item selecionado do menu.
        self.selected_item = 0


    @property
    def start(self):
        curses.wrapper(self.__run)


    # Tira o cursor piscando, define um par de cores e depois desenha a tela.
    def __run(self, screen):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)

        self.__loop(screen)


    # screen é o objeto que desenha as informações na tela. O loop atualiza as informações a todo momento.
    def __loop(self, screen):
        while 1:
            self.__y_len, self.__x_len = screen.getmaxyx()
            screen.clear()

            # Desenha um retângulo na tela.
            rectangle(
                screen, 5, 12,
                self.__y_len - 6, self.__x_len - 15
            )

            self.__show_menu(screen)

            if self.__keyboard(screen):
                break
            else:
                screen.refresh()


    # Desenha os itens do menu centralizados na tela.
    def __show_menu(self, screen):
        for index, text in enumerate(self.menu_list):
            x = self.__x_len // 2 - len(text) // 2
            y = self.__y_len // 2 - len(self.menu_list) // 2 + index

            # Se o ítem for selecionado, ele mostra o item azul.
            if self.selected_item == index:
                screen.attron(curses.color_pair(1))

            screen.addstr(y, x, text)
            screen.attroff(curses.color_pair(1))


    # Detecta as teclas precionadas e retorna True se for uma tecla "return".
    def __keyboard(self, screen):
        key = screen.getch()

        if key in self.keys["up"] and self.selected_item > 0:
            self.selected_item -= 1

        elif key in self.keys["down"] and self.selected_item < len(self.menu_list) - 1:
            self.selected_item += 1

        elif key in self.keys["return"]:
            return True

        return False


class Play(Globals):
    """
     *  PLAY: Além de iniciar o jogo e fazer ele funcionar, essa classe
     *  guarda a pontuação da partida e a data de quando ela começou no
     *  atributo self.score (uma lista).
    """

    def __init__(self, snake_body_fill, apple_fill):
        super().__init__()

        self.__snake_body_fill = snake_body_fill
        self.__apple_fill = apple_fill

        self.__pause = False
        self.score = None


    @property
    def start(self):
        curses.wrapper(self.__run)


    # Configura a taxa de atualização da tela e carrega os "sprites iniciais" na tela.
    def __run(self, screen):
        self.__y_len, self.__x_len = screen.getmaxyx()

        # Setup inicial para a nova screen que será carregada.
        curses.curs_set(False)
        screen.nodelay(True)
        screen.clear()

        # Desenha a área do mapa na tela.
        rectangle(
            screen, 2, 5,
            self.__y_len - 3, self.__x_len - 6
        )

        # Reseta a pontuação.
        self.score = [
            str( datetime.today() ),   # -> Data do começo da partida
            0                          # -> Pontuação da partida
        ]

        # Carrega os elementos e inicia o jogo.
        self.__load_content(screen)
        self.__loop(screen)


    def __loop(self, screen):
        while 1:
            # Se a cobra estiver subindo/descendo, ela vai mais devagar...
            if self.__current_direction in ["up", "down"]:
                screen.timeout(60)
            else:
                screen.timeout(40)

            self.__get_new_direction(screen, self.__current_direction)

            # Se o jogo não estiver pausado, ele continua...
            if not self.__pause:
                self.__move_snake_head(screen)
                self.__remove_the_tail(screen)

            if self.__condictions_to_lose():
                break

            screen.refresh()


    # Cira o corpo da cobra, define uma direção e spawna uma maçã.
    def __load_content(self, screen):
        self.__snake_body = [
            [
                self.__y_len // 2,
                self.__x_len // 2
            ]
        ]

        # Agora, seta uma direção default e spawna uma maçã.
        self.__current_direction = "right"
        self.__spawn_apple(screen)

        # Spawna o corpo (0 e 1) da cobra, com base nas cordenadas da cabeça (0).
        screen.addstr(
            self.__snake_body[0][0],
            self.__snake_body[0][1],
            self.__snake_body_fill
        )


    # Seleciona, aleatoriamente, uma posição na tela, baseado em seu tamanho.
    def __get_apple_position(self):
        while 1:
            apple = [
                random.randint(3, self.__y_len - 4),
                random.randint(6, self.__x_len - 7)
            ]

            # Se a posição cair em cima da cobra, ele gera novamente até encontrar...
            if apple not in self.__snake_body:
                break

        return apple


    # Faz a maçã aparecer na tela e guarda as cordenadas dessa posição.
    def __spawn_apple(self, screen):
        self.apple = self.__get_apple_position()

        screen.addstr(
            self.apple[0], self.apple[1],
            self.__apple_fill
        )


    # Muda de direção, ou não, com base na tecla precionada.
    def __get_new_direction(self, screen, direction):
        key = screen.getch()
        new_direction = None

        # Isso salva a direção da tecla precionada em new_direction...
        for i in self.keys.items():
            if key in i[1]:
                new_direction = i[0]

        # Só muda de direção se a nova direção não for a mesma ou oposta, ou se não for "return"...
        if (
            new_direction in self.keys.keys()
            and new_direction != self.oposite[direction]
            and new_direction != "return"
        ):
            self.__current_direction = new_direction

        # Se a tecla for "return" ele troca os valores de self.__pause...
        elif new_direction == "return":
            if self.__pause:
                self.__pause = False
            else:
                self.__pause = True


    # Desenha uma nova cabeça na frente da cobra, com base na direção atual.
    def __move_snake_head(self, screen):
        self.__snake_head = self.__snake_body[0]

        # Pega as cordenadas da direção atual, com base nas cordenadas da cabeça da cobra.
        if self.__current_direction == "right":
            self.__ghost_snake_head = [self.__snake_head[0], self.__snake_head[1] + 1]

        elif self.__current_direction == "left":
            self.__ghost_snake_head = [self.__snake_head[0], self.__snake_head[1] - 1]

        elif self.__current_direction  == "up":
            self.__ghost_snake_head = [self.__snake_head[0] - 1, self.__snake_head[1]]

        elif self.__current_direction == "down":
            self.__ghost_snake_head = [self.__snake_head[0] + 1, self.__snake_head[1]]

        # Desenha a nova cabeça com as novas cordenadas na tela.
        screen.addstr(
            self.__ghost_snake_head[0],
            self.__ghost_snake_head[1],
            self.__snake_body_fill
        )

        # Depois, salva essas novas cordenadas na lista em memória.
        self.__snake_body.insert(0, self.__ghost_snake_head)


    # Remove a cauda da cobra, tanto em memória quanto em tela, e contar um ponto.
    def __remove_the_tail(self, screen):
        if self.__snake_head == self.apple:
            self.__spawn_apple(screen)

            self.score[1] += 1
            screen.addstr(2, 7, f" Score: {self.score[1]} ")

        else:
            screen.addstr(
                self.__snake_body[-1][0],
                self.__snake_body[-1][1],
                " "
            )

            self.__snake_body.pop()


    # Condições para perder no jogo.
    def __condictions_to_lose(self):
        if (
            # Se a cabeça da cobra bater nas quinas do mapa...
            self.__snake_head[0] <= 2 or self.__snake_head[0] >= self.__y_len - 3
            or self.__snake_head[1] <= 5 or self.__snake_head[1] >= self.__x_len - 6

            # Se a cabeça da cobra bater no seu próprio corpo...
            or self.__ghost_snake_head in self.__snake_body[1:]
        ):
            return 1


class ScoreBoard(Globals):
    """
     *  SCORE BOARD: Armazena todo os histórico de pontuação do jogador,
     *  junto com a data de cada partida. Também é responsável por carregar
     *  e mostrar a lista formatada na tela.
    """

    def __init__(self):
        super().__init__()
        self.__score_list = list()
        # self.__score_list = [["lafjkdslfjadslf", 123], ["lafjkdslfjadslf", 123], ["lafjkdslfjadslf", 123]]
        self.__y_value = 3
        self.__x_value = 7


    @property
    def start(self):
        curses.wrapper(self.__run)


    def __run(self, screen):
        curses.curs_set(False)
        screen.clear()

        self.__loop(screen)


    def __loop(self, screen):
        while 1:
            for key, value in enumerate(self.__score_list):
                # Isso garante que a lista será escrita na tela toda...
                try:
                    screen.addstr(
                        self.__y_value + key,
                        self.__x_value,
                        f"[{value[0]}] >>> {value[1]}"
                    )
                except:
                    pass

            # Se qualquer tecla for precionada, o loop será interrompido.
            self.__key = screen.getch()

            if self.__key in self.keys["return"]:
                break


    def add_score(self, score):
        # Se a lista estiver vazia, basta anexar o único score registrado.
        if len(self.__score_list) == 0:
            self.__score_list.append(score)
            return

        # Procura uma posição para adicionar o novo valor.
        for key, value in enumerate(self.__score_list):
            if score[1] > value[1]:
                self.__score_list.insert(key, score)
                break

            elif score[1] == value[1]:
                self.__score_list.insert(key + 1, score)
                break

            elif key == len(self.__score_list) - 1:
                self.__score_list.append(score)
                break


