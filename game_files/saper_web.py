
import random
from copy import deepcopy
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


def transform_matrix(in_matrix):
    matrix = deepcopy(in_matrix)
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
        self.count_close = 1
        self.difficulty = difficulty

    def create_matrix(self, difficulty):
        if difficulty == 'diffEasy':
            self.width, self.height, self.count_close, self.count_close, self.count_mins = Easy()
        elif difficulty == 'diffMed':
            self.width, self.height, self.count_close, self.count_close, self.count_mins = Medium()
        elif difficulty == 'diffHard':
            self.width, self.height, self.count_close, self.count_close, self.count_mins = Hard()
        self.matrix = [['■' for _ in range(self.width)] for _ in range(self.height)]
        self.transformed_matrix = transform_matrix(self.matrix)

    def interactive(self, move, cords):
        if move == 'open':
            var = 1
        elif move == 'flag':
            var = 2
        if not self.mas_of_mins:
            self.mas_of_mins = self.random_place_of_mins(*cords)
        if var == 1:
            
            if (cords[0], cords[1]) in self.mas_of_mins:  # Обработка поражения, если координаты пользователя равны
                                                            # координатам из списка мин
                self.show_min_on_matrix()
                return 'Вы проиграли!'
            self.check_act(*cords)  # Вызов функции обработки действия
        elif var == 2:
            if self.matrix[cords[0]][cords[1]] == '⚐':
                self.matrix[cords[0]][cords[1]] = '■'
                self.count_close -= 1
            else:
                self.matrix[cords[0]][cords[1]] = '⚐'
                self.count_close += 1
            if self.mas_of_mins and self.is_victory():  # Обработка победы, если все клетки закрыты
                self.show_min_on_matrix()
                return ('Вы выиграли!', self.difficulty)
        self.transformed_matrix = transform_matrix(self.matrix)
        return

    def is_victory(self):       # Обработка победы, если координаты флажков соотвествуют кооржинатам мин
        flag_coords = set()
        for y in range(len(self.matrix)):
            for x in range(len(self.matrix[y])):
                if self.matrix[y][x] == '⚐':
                    flag_coords.add((y, x))
        if flag_coords == set(self.mas_of_mins):
            return True

    def random_place_of_mins(self, row, col):
        # Рандомно создает кординаты мин на поле, после идет проверка не совпадают ли
        # координаты мины и первой открытой клетки
        mas_of_mins = []
        while len(mas_of_mins) < self.count_mins:  # Цикл работает пока во множестве меньше элементов чем количество мин
            row_min, col_min = random.randint(0, self.height - 1), random.randint(0, self.width - 1)
            if (row_min, col_min) != (row, col):  # Проверка не координаты мины и=с координатами первой открытой клетки
                mas_of_mins.append((row_min, col_min))
        return mas_of_mins
        #self.mas_of_mins = self.mas_of_mins  # Превращает множество в список, для моего удобства :)

    def show_min_on_matrix(self):
        for i in self.mas_of_mins:
            self.matrix[i[0]][i[1]] = '@'
        self.transformed_matrix = transform_matrix(self.matrix)

    def check_act(self, row, col):
        count_mins = self.check_min_around(row, col)  #Рекурсивная функция обрабатывающая каждое открытие клетки
        if count_mins:  # Если значение не равно 0 то мы присваеваем это значение клетке
            self.matrix[row][col] = count_mins
        else:  # Иначе присваеваем пустоту и повторяем в соседних клетках
            self.matrix[row][col] = ' '
            for i in range(row - 1, row + 2):
                for j in range(col - 1, col + 2):
                    if 0 <= i < self.height and 0 <= j < self.width:  # Если координаты не находятся за пределами поля
                        if self.matrix[i][j] == '■':  # И значение ячейки равно этому символу (для окончания рекурсии
                            # и правильного подсчета закрытых клеток)
                            self.check_act(i, j)  # То мы рекурсивно вызываем функцию с этими координатами
                            self.count_close += 1

    def check_min_around(self, row, col):
    # С помощью счетчика count подсчитывает количество мин в 8 окружающих клетках'''
        count = 0
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if 0 <= i <= self.height - 1 and 0 <= j <= self.width - 1:
                    if (i, j) in self.mas_of_mins:
                        count += 1
        return count



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