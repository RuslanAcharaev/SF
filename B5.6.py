def intro():
    print('Добро пожаловать в игру "Крестики-Нолики"')

def print_field():
    print('    ', end='')
    for col in range(1, 4):
        print(f'{col:2}', end=' ')
    print()

    letters = 'abc'
    for i, row in enumerate(field, start=1):
        print(f'{letters[i-1]:2} |', end=' ')
        for value in row:
            print(f'{value:2}', end=' ')
        print()

def game_input():
    while True:
        letters = 'abc'
        digits = '123'
        row = input("Введите букву строки: ")
        if len(row) != 1:
            print("Введите одно значение!")
            continue

        if row not in letters:
            print("Введите обозначение строки (a, b или c)")
            continue

        col = input("Введите номер столбца: ")
        if len(col) != 1:
            print("Введите одно значение!")
            continue

        if col not in digits:
            print("Введите номер столбца (1, 2 или 3)")
            continue

        row, col = letters.find(row), digits.find(col)

        if field[row][col] != "-":
            print(" Клетка занята! ")
            continue

        return row, col

def winners_check(field):
    for row in field:
        if row[0] == row[1] == row[2] and row[0] != "-":
            return row[1]

    for col in range(0, 3):
        if field[0][col] == field[1][col] == field[2][col] and field[0][col] != "-":
            return field[0][col]

    if field[0][0] == field[1][1] == field[2][2] and field[0][0] != "-":
        return field[0][0]
    if field[0][2] == field[1][1] == field[2][0] and field[0][2] != "-":
        return field[0][2]

    return None

def gameplay():
    count = 0
    while True:
        count += 1
        print_field()
        if count % 2 == 1:
            print('Ход игрока "X"!')
        else:
            print('Ход игрока "0"!')

        row, col = game_input()

        if count % 2 == 1:
            field[row][col] = "X"
        else:
            field[row][col] = "0"

        if winners_check(field):
            print('------------')
            print_field()
            print('------------')
            print(f"Победил игрок {winners_check(field)}!!!")
            play_again()
            break

        if count == 9:
            print('------------')
            print_field()
            print('------------')
            print("Ничья!")
            play_again()
            break

def play_again():
    again = input("Играть еще? (Y/N): ")
    if again == 'Y' or again == 'y':
        global field
        field = [['-' for col in range(3)] for row in range(3)]
        gameplay()
    else:
        return print("Спасибо за игру!")

intro()
field = [['-' for col in range(3)] for row in range(3)]
gameplay()
