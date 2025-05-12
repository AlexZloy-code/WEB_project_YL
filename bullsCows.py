import random as r


def generate_answer():
        while True:
            num = str(r.randint(1000, 9999))
            if len(set(num)) == 4:  # Все цифры разные
                return num


class BullsCows():
    def __init__(self):
        self.history = []  # История попыток в формате [(число, коровы, быки), ...]
        self.answer = generate_answer()  # Загаданное число (4 цифры, уникальные)
    
    def make_guess(self, guess):
        '''
        Принимает догадку (4-значное число) и возвращает результат.
        
        Возвращает:
        - Если угадано: {'status': 'win', 'bulls': 4, 'cows': 0}
        - Если не угадано: {'status': 'guess', 'bulls': X, 'cows': Y}
        - Если ошибка: {'status': 'error', 'message': '...'}
        '''
        if not isinstance(guess, str) or len(guess) != 4 or not guess.isdigit():
            return {'status': 'error', 'message': 'Число должно быть 4-значным!'}
        
        if len(set(guess)) != 4:
            return {'status': 'error', 'message': 'Цифры должны быть уникальными!'}
        
        bulls, cows = 0, 0
        for i in range(4):
            if self.answer[i] == guess[i]:
                bulls += 1
            elif guess[i] in self.answer:
                cows += 1
        
        self.history.append(f'Попытка: {guess}<br>Коров: {cows}, быков: {bulls}')
        
        if bulls == 4:
            return {'status': 'win', 'message': 'Вы выиграли!'}
        else:
            return {'status': 'guess', 'message': self.history}