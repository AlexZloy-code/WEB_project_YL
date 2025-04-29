import random


def random_place_of_mins(row, col):
    '''Рандомно создает кординаты мин на поле, после идет проверка не совпадают ли \
    координаты мины и первой открытой клетки'''
    global mas_of_mins, count_mins
    while len(mas_of_mins) < count_mins:  # Цикл работает пока во множестве меньше элементов чем количество мин
        row_min, col_min = random.randint(0, height - 1), random.randint(0, width - 1)
        if (row_min, col_min) != (row, col):  # Проверка не координаты мины и=с координатами первой открытой клетки
            mas_of_mins.add((row_min, col_min))
    mas_of_mins = list(mas_of_mins)  # Превращает множество в список, для моего удобства :)
    return mas_of_mins


def check_min_around(row, col):
    ''' С помощью счетчика count подсчитывает количество мин в 8 окружающих клетках'''
    count = 0
    for i in range(row - 1, row + 2):
        for j in range(col - 1, col + 2):
            if 0 <= i <= height - 1 and 0 <= j <= width - 1:
                if (i, j) in mas_of_mins:
                    count += 1
    return count


def check_act(row, col):
    '''Рекурсивная функция обрабатывающая каждое открытие клетки'''
    global matrix, count_close
    count_mins = check_min_around(row, col)
    if count_mins:  # Если значение не равно 0 то мы присваеваем это значение клетке
        matrix[row][col] = count_mins
        count_close -= 1
    else:  # Иначе присваеваем пустоту и повторяем в соседних клетках
        matrix[row][col] = ' '
        count_close -= 1
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if 0 <= i < height and 0 <= j < width:  # Если координаты не находятся за пределами поля
                    if matrix[i][j] == '■':  # И значение ячейки равно этому символу (для окончания рекурсии
                        # и правильного подсчета закрытых клеток)
                        check_act(i, j)  # То мы рекурсивно вызываем функцию с этими координатами


def show_matrix():
    '''Вывод двумерного массива (поля)'''
    for line in matrix:
        print(*line, sep='  ')
    return matrix


def show_min_on_matrix():
    '''Замена всех мин поля на другой символ'''
    global matrix
    for i in mas_of_mins:
        matrix[i[0]][i[1]] = '@'
    show_matrix()


def varible_znach():
    global width, height, count_close, count_mins
    while True:  # Максимальная проверка на корректность введения размеров поля
        size = input('Введите размеры поля через пробел (ширина высота): ')
        if len(size.split()) != 2:
            print("Данные введены некорректно, введено не 2 числа, либо разделителем является не пробел!")
            continue
        width, height = size.split()
        if not width.isdigit():
            print("Данные введены некорректно, 1 значение не является числом")
            continue
        elif not height.isdigit():
            print("Данные введены некорректно, 2 значение не является числом")
            continue
        width, height = map(int, size.split())
        break
    count_close = width * height  # Создаём поле с размерами от пользователя

    count_mins = input('Введите количество мин на поле: ')  # Ввод количества мин и дальнейшая проверка данных
    while not count_mins.isdigit():
        print('Данные введены некорректно, введено не число')
        count_mins = input('Введите количество мин на поле: ')
    count_mins = int(count_mins)
    while count_mins >= width * height:
        print('Данные введены некорректно, количество мин не должно превышать или быть равным количеству ячеек')
        count_mins = int(input('Введите количество мин на поле: '))


def Easy():
    #global width, height, count_close, count_mins     
    width, height, count_close, count_mins = 5, 5, 25, 7
    return width, height, count_close, count_close, count_mins

    
def Medium():
    #global width, height, count_close, count_mins
    width, height, count_close, count_mins = 8, 8, 64, 10
    return width, height, count_close, count_close, count_mins


def Hard():
    #global width, height, count_close, count_mins
    width, height, count_close, count_mins = 16, 16, 256, 40
    return width, height, count_close, count_close, count_mins

def main():
    print('Здравствуйте, вас приветсвует программа "Сапёр", пожалуйста выберете уровень сложности игры:')
    print('1 - Лёгкий', '2 - Средний', '3 - Сложный', '4 - Настраеваемый пользователем', sep='\n')
    var = input()
    while var not in '1234':
        print('Данные введены некорректно')
        var = input()
    var, width, height, count_close, count_mins = int(var), 0, 0, 0, 0
    if var == 1:
        Easy()
    elif var == 2:
        Medium()
    elif var == 3:
        Hard()
    else:
        varible_znach()

    mas_of_mins = set()  # Создание пустого множества для координат мин
    matrix = [['■' for _ in range(width)] for _ in range(height)]  # Создание "визуального" поля

    while True:
        if count_close == count_mins:  # Обработка победы, если количество не раскрытых клеточек равно колличеству мин
            show_min_on_matrix()
            print('Вы выиграли')
            break
        show_matrix()
        while True:  # Максимальная проверка на корректность введения координат
            cords = input('Введите координаты ячейки начиная с единицы через пробел (ряд колонка): ').split()
            if len(cords) != 2:
                print("Данные введены некорректно, введено не 2 числа, либо разделителем является не пробел!")
                continue
            cords = cords
            if not cords[0].isdigit():
                print("Данные введены некорректно, 1 значение не является числом")
                continue
            elif not cords[1].isdigit():
                print("Данные введены некорректно, 2 значение не является числом")
                continue
            cords = list(map(int, cords))
            if not 0 < cords[0] <= height:
                print("1 значение некорректно")
                continue
            elif not 0 < cords[1] <= width:
                print("2 значение некорректно")
                continue
            if matrix[cords[0] - 1][cords[1] - 1] == ' ' or matrix[cords[0] - 1][cords[1] - 1] in range(1, 9):
                print('Клетка уже открыта')
                continue
            break
        cords = [i - 1 for i in cords]  # Переработка данных пользователя для работы с индексамии
        print('Выберите действие из списка:', '1 - открыть клетку', '2 - пометить флажком',
            '3 - пометить вопросом', sep='\n')
        var = input()
        while var not in '123':
            print('Данные введены некорректно')
            var = input()
        if var == '1':
            if matrix[cords[0]][cords[1]] in ('?', u'\u2690'):
                print('Вы уверены что хотите открыть?', '1 - Да', '2 - Нет', sep='\n')
                var = input()
                while var not in '12':
                    print('Данные введены некорректно')
                    var = input()
                if var == '2':
                    continue
            if not mas_of_mins:  # Если список мин пуст (первый ход), то он будет создан
                random_place_of_mins(*cords)
            if (cords[0], cords[1]) in mas_of_mins:  # Обработка поражения, если координаты пользователя равны
                # координатам из списка мин
                show_min_on_matrix()
                print('Вы проиграли!')
                break
            check_act(*cords)  # Вызов функции обработки действия
        elif var == '2':
            matrix[cords[0]][cords[1]] = u'\u2690'
        elif var == '3':
            matrix[cords[0]][cords[1]] = '?'


if __name__=='__main__':
    main()