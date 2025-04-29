import saper_console as sc
from flask import Flask, render_template, redirect


class Cell(): # Я подумал что лучше сделать каждую клетку классом, посмотрим, как потом можно развить идею
    def __init__(self, type, value='', image=None):
        self.type = type
        self.value = value


class DiffButton():
    def __init__(self, value, href, type, styles=None):
        self.value = value
        self.href = href
        self.type = type


def transform_matrix(matrix):
    translator = {'■': ('closed', ''), '@': ('mine', ''), ' ': ('opened', ''), '⚐': ('flaged', '⚐')}
    for y in range(len(matrix)):
        for x in range(len(matrix[y])):
            try:
                int(matrix[y][x])
                matrix[y][x] = Cell('opened', matrix[y][x])
            except ValueError:
                matrix[y][x] = Cell(*translator[matrix[y][x]])
    return matrix
            

class Minesweeper():
    def __init__(self, difficulty):
        self.message = 'Здравствуйте, вас приветсвует программа "Сапёр", пожалуйста выберете уровень сложности игры:'
        self.create_matrix(difficulty)
        self.mas_of_mins = []
        self.selected_cell_id = []

    def create_matrix(self, difficulty):
        if difficulty == 'diffEasy':
            self.width, self.height, self.count_close, self.count_close, self.count_mins = sc.Easy()
        elif difficulty == 'diffMed':
            self.width, self.height, self.count_close, self.count_close, self.count_mins = sc.Medium()
        elif difficulty == 'diffHard':
            self.width, self.height, self.count_close, self.count_close, self.count_mins = sc.Hard()
        self.matrix = transform_matrix([['■' for _ in range(self.width)] for _ in range(self.height)])

    def gameplay(self):
        while True:
            if self.count_close == self.count_mins:  # Обработка победы, если количество не раскрытых клеточек равно колличеству мин
                self.matrix = transform_matrix(sc.show_min_on_matrix())
                print('Вы выиграли')
                return 'Victory'
            self.matrix = transform_matrix(sc.show_matrix())

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
                if not 0 < cords[0] <= sc.height:
                    print("1 значение некорректно")
                    continue
                elif not 0 < cords[1] <= sc.width:
                    print("2 значение некорректно")
                    continue
                if sc.matrix[cords[0] - 1][cords[1] - 1] == ' ' or sc.matrix[cords[0] - 1][cords[1] - 1] in range(1, 9):
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
                if sc.matrix[cords[0]][cords[1]] in ('?', u'\u2690'):
                    print('Вы уверены что хотите открыть?', '1 - Да', '2 - Нет', sep='\n')
                    var = input()
                    while var not in '12':
                        print('Данные введены некорректно')
                        var = input()
                    if var == '2':
                        continue
                if not self.mas_of_mins:  # Если список мин пуст (первый ход), то он будет создан
                    self.mas_of_mins = sc.random_place_of_mins(*cords)
                if (cords[0], cords[1]) in sc.mas_of_mins:  # Обработка поражения, если координаты пользователя равны
                    # координатам из списка мин
                    sc.show_min_on_matrix()
                    print('Вы проиграли!')
                    break
                sc.check_act(*cords)  # Вызов функции обработки действия
            elif var == '2':
                sc.matrix[cords[0]][cords[1]] = u'\u2690'
            elif var == '3':
                sc.matrix[cords[0]][cords[1]] = '?'