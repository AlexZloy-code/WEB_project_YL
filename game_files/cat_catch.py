import random
from copy import deepcopy

class CatCatch():
    def __init__(self):
        self.cat = Cat()
        self.matrix = self.create_matrix()
        self.transformed_matrix = transform_matrix(self.matrix)

    def create_matrix(self):
        random_cords = []
        fill_count = 12
        field_size = 11
        matrix = [[0 for _ in range(field_size)] for _ in range(field_size)]
        for _ in range(fill_count):
            cord = [5, 5]
            while cord in random_cords or cord == [5, 5]:
                cord = [random.randint(0, 11), random.randint(0, 11)]
            random_cords.append(cord)
        for x in range(field_size):
            for y in range(field_size):
                if [x, y] in random_cords:
                    matrix[x][y] = 1
        matrix[self.cat.cords[0]][self.cat.cords[1]] = 2
        return matrix

    def interact(self, fill):
        if not fill:
            return {'status': 'error', 'field': deepcopy(self.transformed_matrix)}
        self.matrix[fill[0]][fill[1]] = 1
        path, is_lose = self.cat.find_cat_path(self.matrix)
        if is_lose:
            self.transformed_matrix = transform_matrix(self.matrix)
            return {'status': 'lose', 'field': deepcopy(self.transformed_matrix)}
        if not path:
            self.transformed_matrix = transform_matrix(self.matrix)
            return {'status': 'win', 'field': deepcopy(self.transformed_matrix)}
        self.matrix[self.cat.cords[0]][self.cat.cords[1]] = 0
        self.cat.cords = path[0]
        self.matrix[self.cat.cords[0]][self.cat.cords[1]] = 2
        self.transformed_matrix = transform_matrix(self.matrix)
        return {'status': 'moving', 'field': deepcopy(self.transformed_matrix)}
    

def transform_matrix(in_matrix):
    matrix = deepcopy(in_matrix)
    translator = {0: 'opened', 1: 'closed', 2: 'cat'}
    for x in range(len(matrix)):
        for y in range(len(matrix[x])):
            matrix[x][y] = f'''<a class="cat-field-block {translator[matrix[x][y]]} col" href="javascript:interact_cell('{x} {y}')"></a>'''
    return matrix


class Cat():
    def __init__(self):
        self.cords = [5, 5]

    def find_cat_path(self, matrix):      # эту дичь надо потом как то объянить, это что то типо волнового алгоритма
        directions1 = [(-1, 0), (0, -1), (0, 1), (1, 0), (-1, 1), (1, 1)]
        directions2 = [(-1, 0), (0, -1), (0, 1), (1, 0), (1, -1), (-1, -1)]
        rows = len(matrix)
        cols = len(matrix[0])
        
        queue = []
        queue.append((self.cords[0], self.cords[1]))
        
        # Откуда пришли в каждую клетку (для восстановления пути)
        parent = [[None for _ in range(cols)] for _ in range(rows)]
        
        # Посещённые клетки
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        visited[self.cords[0]][self.cords[1]] = True
        
        found_exit = None
        is_lose = False
        count = 0
        while queue:
            row, col = queue.pop(0)  # Берём первую клетку из очереди
            count += 1
            # Проверяем, не на краю ли мы
            if row == 0 or row == rows - 1 or col == 0 or col == cols - 1:
                if count == 1:
                    is_lose = True
                found_exit = (row, col)
                break
            if row % 2 == 0:
                directions = directions2
            else:
                directions = directions1
            # Проверяем все направления
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                # Если клетка в пределах поля, свободна и не посещена
                if (0 <= new_row < rows and 0 <= new_col < cols and
                    matrix[new_row][new_col] == 0 and not visited[new_row][new_col]):
                    visited[new_row][new_col] = True
                    parent[new_row][new_col] = (row, col)
                    queue.append((new_row, new_col))
        
        # Восстанавливаем путь (от выхода к коту)
        path = []
        if found_exit:
            current = found_exit
            while current != self.cords:  # Убираем `or not current`
                path.append(current)
                current = parent[current[0]][current[1]]
                if current is None:  # Защита от зацикливания
                    break
            path.reverse()  # Разворачиваем, чтобы получить путь от кота к краю
        
        return path, is_lose
                

    
if __name__ == '__main__':
    game = CatCatch()
    print(game.matrix)