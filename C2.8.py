from random import randint, choice


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за пределы доски"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


# Класс игровых правил, где можно задать размер стороны поля, набор кораблей
class GameRules:
    letters = "ABCDEFGHI"
    size = 6
    letters = letters[:size]
    ships_lenghts = [3, 2, 2, 1, 1, 1, 1]


# Класс клетки на игровом поле, для простого изменения внешнего вида
class Cell(object):
    empty_cell = "\033[37mO\033[0m"
    ship_cell = "\033[34m■\033[0m"
    contour_cell = "\033[37m.\033[0m"
    ship_destroyed = "\033[31mX\033[0m"
    ship_damaged = "\033[33mX\033[0m"
    miss_cell = "\033[32mT\033[0m"


class Dot:
    # Класс "точки" для хранения координат
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Метод для сравнения координат
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # Метод для вывода координат в консоль
    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    # Класс корабля с информацией о нахождении носовой части,
    # длине, ориентации в пространстве, оставшихся жизнях
    def __init__(self, bow, length, o):
        self.bow = bow
        self.length = length
        self.o = o
        self.lives = length

    # Координаты корабля
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            elif self.o == 2:
                cur_x -= i

            elif self.o == 3:
                cur_y -= i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    # Класс игрового поля с информацией о расположении кораблей

    def __init__(self, hid=False):
        # self.size = size

        self.hid = hid

        self.count = 0

        self.field = [[Cell.empty_cell] * GameRules.size for _ in range(GameRules.size)]
        self.priority = [[1 for _ in range(GameRules.size)] for _ in range(GameRules.size)]

        self.busy = []
        self.ships = []

    # Внешний вид игрового поля
    def __str__(self):
        res = ""
        head = ""
        for i in GameRules.letters:
            head += f" {GameRules.letters.find(i) + 1} |"
        res += "  |" + f"{head}"
        for i, row in enumerate(self.field):
            res += f"\n{GameRules.letters[i]} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace(Cell.ship_cell, Cell.empty_cell)
        return res

    # Проверка границ игрового поля
    def out(self, d):
        return not ((0 <= d.x < GameRules.size) and (0 <= d.y < GameRules.size))

    # Метод для корректного размещения на игровом поле
    # и для отрисовки контура потопленного корабля
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = Cell.contour_cell
                    self.busy.append(cur)

    # Метод добавления корабля на игровое поле
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = Cell.ship_cell
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # Выстрел с проверками на границы игрового поля, повторный выстрел
    # И результаты выстрела (подбил, потопил, промахнулся)
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = Cell.ship_damaged
                if ship.lives == 0:
                    self.count += 1
                    for d in ship.dots:
                        self.field[d.x][d.y] = Cell.ship_destroyed
                    self.contour(ship, verb=True)
                    print("Корабль потоплен!")
                    return False
                else:
                    print("Корабль подбит!")
                    return True

        self.field[d.x][d.y] = Cell.miss_cell
        print("Промах!")
        return False

    # Расстановка приоритетов для ИИ с целью запретить повторно стрелять в
    # одни и те же клетки, а также с целью повысить способность добивать
    # уже подбитые корабли
    def recalculate_priority(self):
        # По умолчанию приоритет для всех клеток равен единице
        self.priority = [[1 for _ in range(GameRules.size)] for _ in range(GameRules.size)]

        # Для клеток с промахами, подбитыми и потопленными кораблями устанавливаем
        # нулевой приоритет.
        for x in range(GameRules.size):
            for y in range(GameRules.size):
                if self.field[x][y] == Cell.ship_damaged:
                    self.priority[x][y] = 0
                    # Для подбитых кораблей дополнительно увеличиваем приоритет
                    # для клеток по вертикали и горизонтали и обнуляем приоритет
                    # диагональных клеток
                    if x - 1 >= 0:
                        if y - 1 >= 0:
                            self.priority[x - 1][y - 1] = 0
                        self.priority[x - 1][y] *= 10
                        if y + 1 < GameRules.size:
                            self.priority[x - 1][y + 1] = 0
                    if y - 1 >= 0:
                        self.priority[x][y - 1] *= 10
                    if y + 1 < GameRules.size:
                        self.priority[x][y + 1] *= 10
                    if x + 1 < GameRules.size:
                        if y - 1 >= 0:
                            self.priority[x + 1][y - 1] = 0
                        self.priority[x + 1][y] *= 10
                        if y + 1 < GameRules.size:
                            self.priority[x + 1][y + 1] = 0

                if self.field[x][y] == Cell.miss_cell:
                    self.priority[x][y] = 0

                if self.field[x][y] == Cell.ship_destroyed:
                    self.priority[x][y] = 0
                    # Для потопленных кораблей дополнительно обнуляем приоритет
                    # по контуру
                    if x - 1 >= 0:
                        if y - 1 >= 0:
                            self.priority[x - 1][y - 1] = 0
                        self.priority[x - 1][y] = 0
                        if y + 1 < GameRules.size:
                            self.priority[x - 1][y + 1] = 0
                    if y - 1 >= 0:
                        self.priority[x][y - 1] = 0
                    if y + 1 < GameRules.size:
                        self.priority[x][y + 1] = 0
                    if x + 1 < GameRules.size:
                        if y - 1 >= 0:
                            self.priority[x + 1][y - 1] = 0
                        self.priority[x + 1][y] = 0
                        if y + 1 < GameRules.size:
                            self.priority[x + 1][y + 1] = 0

    # Получение списка координат с наивысшим приоритетом
    def get_max_priority_cords(self):
        max_priority = max(max(self.priority, key=max))
        cords = []
        for x in range(len(self.priority)):
            for y in range(len(self.priority[0])):
                if self.priority[x][y] == max_priority:
                    cords.append((x, y))

        return cords

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    # Класс игрока
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    # Класс ИИ. Запускает пересчет приоритетов клеток и случайным образом выбирает
    # цель из списка координат клеток с наивысшим приоритетом
    def ask(self):
        self.enemy.recalculate_priority()
        p = choice(self.enemy.get_max_priority_cords())
        x, y = p[0], p[1]
        d = Dot(x, y)
        print(f"Ход компьютера: {GameRules.letters[d.x]}{d.y + 1}")
        return d


class User(Player):
    # Класс пользователя
    def ask(self):
        while True:
            cords = input("Ваш ход: ").upper().replace(" ", "")

            if len(cords) != 2:
                print(" Введите 2 значения! ")
                continue

            x, y = cords[0].upper(), cords[1:]

            if x not in GameRules.letters or not y.isdigit() or int(y) not in range(1, len(GameRules.letters) + 1):
                print(" Ошибка формата данных! Введите букву строки и номер столбца. ")
                continue

            x, y = GameRules.letters.index(x), int(y)

            return Dot(x, y - 1)


# Класс игрового процесса
class Game:
    def __init__(self):

        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board()
        attempts = 0
        for ship_l in GameRules.ships_lenghts:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, GameRules.size), randint(0, GameRules.size)), ship_l, randint(0, 3))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass

        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    @staticmethod
    def greeting():
        print('-' * (GameRules.size * 8 + 14))
        print(' ' * int((GameRules.size * 8 - 24) / 2) + 'Добро пожаловать в игру "Морской бой"!')
        print('-' * (GameRules.size * 8 + 14))
        print('Ввод данных: xy, где x - буква строки, y - номер столбца')

    @staticmethod
    def print_boards(first, second):
        first_sp = first.split("\n")
        second_sp = second.split("\n")
        text = []
        for f, s in zip(first_sp, second_sp):
            text.append(f"{f}   ||   {s}")

        return "\n".join(text)

    def draw_boards(self):
        print('-' * (GameRules.size * 8 + 14))
        line = "-" * (GameRules.size * 4 + 3)
        us_board = f"Доска пользователя:{' ' * (GameRules.size * 4 - 16)}\n" + line + '\n' + str(self.us.board)
        ai_board = "Доска компьютера:\n" + line + '\n' + str(self.ai.board)

        print(self.print_boards(us_board, ai_board))

    def loop(self):
        num = 0
        while True:
            self.draw_boards()

            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.draw_boards()
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.defeat():
                self.draw_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greeting()
        self.loop()


if __name__ == '__main__':
    g = Game()
    g.start()
