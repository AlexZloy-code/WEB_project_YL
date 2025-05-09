import random as r


def game_handler(answer, num, digits, difficulty, posled):
    if difficulty == 'Easy':
        cows, bows = 0, 0
        for i in range(4):
            if answer[i] == num[i]:
                bows += 1
            elif num[i] in answer:
                cows += 1
        posled.append([num, cows, bows])
        if bows == 4:
            return 'Победа'
        else:
            return posled
    else:
        cows, bows = 0, 0
        for i in range(4):
            if answer[i] == num[i]:
                bows += 1
            elif num[i] in answer:
                cows += 1
        posled.append([num, cows, bows])
        if bows == 4:
            return 'Победа'
        else:
            while True:
                proba = str(
                    r.randint(10 ** (digits - 1), 10 ** digits) - 1)
                if proba in [i[0] for i in posled]:
                    continue
                if len(set(proba)) != len(proba):
                    continue
                flag = True
                for ans in posled:
                    cows_nado, bows_nado = ans[1], ans[2]
                    cows, bows = 0, 0
                    for inx in range(4):
                        if ans[0][inx] == proba[inx]:
                            bows += 1
                        elif proba[inx] in ans[0]:
                            cows += 1
                    if cows != cows_nado or bows != bows_nado:
                        flag = False
                if flag:
                    break
            answer = proba
            return (answer, posled)
