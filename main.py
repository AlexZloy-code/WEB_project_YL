import datetime
import random as r

from game_files.saper_web import Minesweeper
from game_files.diction_for_b_a_c import nums
from game_files.cat_catch import CatCatch

from flask import Flask, render_template, redirect, request, jsonify, make_response, session, url_for
from forms.user import LoginForm, RegisterForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session

from data import db_session
from data.users import User


app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

app.config["SESSION_FILE_DIR"] = "./flask_session_cache"
app.config['SECRET_KEY'] = 'DONT_KNOW_WHAT_TO_WRITE_HERE'
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/users.db")


def main():
    pass


@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    return render_template("mainfiles/index.html", title='Главная')


#      БЫКИ И КОРОВЫ
@app.route('/bulls_and_cows/make_guess', methods=['POST'])
def make_guess():
    data = request.get_json()
    digits = session['b_a_c']['digits']
    difficulty = session['b_a_c']['difficulty']
    num = data['number']
    if difficulty == 'easy':
        cows, bows = 0, 0
        for i in range(digits):
            if session["b_a_c"]['num'][i] == num[i]:
                bows += 1
            elif num[i] in session["b_a_c"]['num']:
                cows += 1
        if [num, cows, bows] in session["b_a_c"]['attempts']:
            session["b_a_c"]['attempts'].remove([num, cows, bows])
        session["b_a_c"]['attempts'].append([num, cows, bows])
        if bows == digits:
            print('win')
            session.pop('b_a_c', None)
            return jsonify({'html': '<h3>Вы выиграли!</h3>', 'status': 'win'})
    else:
        cows, bows = 0, 0
        for i in range(digits):
            if session["b_a_c"]['num'][i] == num[i]:
                bows += 1
            elif num[i] in session["b_a_c"]['num']:
                cows += 1
        if [num, cows, bows] in session["b_a_c"]['attempts']:
            session["b_a_c"]['attempts'].remove([num, cows, bows])
        session["b_a_c"]['attempts'].append([num, cows, bows])
        if bows == digits:
            print('win')
            session.pop('b_a_c', None)
            return jsonify({'html': '<h3>Вы выиграли!</h3>', 'status': 'win'})
        else:
            for proba in nums[str(digits)]:
                proba = str(proba)
                if proba in [i[0] for i in session["b_a_c"]['attempts']]:
                    continue
                flag = True
                for ans in session["b_a_c"]['attempts']:
                    cows_nado, bows_nado = ans[1], ans[2]
                    cows, bows = 0, 0
                    for inx in range(digits):
                        if ans[0][inx] == proba[inx]:
                            bows += 1
                        elif proba[inx] in ans[0]:
                            cows += 1
                    if cows != cows_nado or bows != bows_nado:
                        flag = False
                if flag:
                    break
            session["b_a_c"]['num'] = proba
        #a = {'html': ''.join(['<tr>' + ''.join([f'<td>{i}</td>' for i in j]) + '</tr>' for j in session['b_a_c']['attempts'][::-1]]), 'status': 'guess'}
    return jsonify({'html': ''.join(['<tr>' + ''.join([f'<td>{i}</td>' for i in j]) + '</tr>'
                                                  for j in session['b_a_c']['attempts'][::-1]]),
                                                  'status': 'guess'})


@app.route('/bulls_and_cows', methods=['GET', 'POST'])
def bulls_and_cows():
    if 'b_a_c' in session:
        if request.method == 'GET':
            return render_template('b_a_c/b_a_c_game.html',
                                   history=session["b_a_c"]['attempts'],
                                   digits=session['b_a_c']['digits'])

        return redirect(url_for('bulls_and_cows'))

    if request.method == 'POST':
        digits = int(request.form.get('digits', 4))
        difficulty = request.form.get('difficulty', 'easy')
        proba = str(r.randint(10**(digits-1), 10**digits - 1))
        while len(set(proba)) != digits:
            proba = str(r.randint(10**(digits-1), 10**digits - 1))
        
        session["b_a_c"] = {
            'num': proba,
            'attempts': [],
            'digits': digits,
            'difficulty': difficulty,
            'game_started': True
        }
        session.modified = True

        return redirect(url_for('bulls_and_cows'))
    
    return render_template('b_a_c/b_a_c_menu.html')


#          САПЕР
@app.route('/minesweeper')
def minesweeper():
    if "minesweeper" in session:
        game = session["minesweeper"]
        return render_template('minesweeper/minesweeper.html', field=game.transformed_matrix, title='Сапер')
    return render_template('minesweeper/minesweeper.html', start=True, field=[], title='Сапер')

@app.route('/minesweeper/start', methods=['POST'])
def start_game():
    data = request.get_json()

    if "minesweeper" not in session:
        session["minesweeper"] = Minesweeper(data['field'])  # Создаём игру один раз для сессии
    game = session["minesweeper"]

    return jsonify({'field': render_template('minesweeper/minesweeper.html', field=game.transformed_matrix, title='Сапер')})


@app.route('/minesweeper/select-cell', methods=['POST'])
def select_cell():
    game = session['minesweeper']
    data = request.get_json()
    cell_id = x, y = list(map(int, data['id_cell'].split('-')))
    game.selected_cell_id = cell_id
    print(cell_id)
    return jsonify({'id_cell': str(cell_id),
                    'cell_type': game.transformed_matrix[y][x].type})


@app.route('/minesweeper/interact', methods=['POST'])
def interact_cell():
    game = session['minesweeper']
    y, x = game.selected_cell_id
    data = request.get_json()
    msg = game.interactive(data['interact_type'], [x, y])
    field = game.transformed_matrix

    # При выигрыше/проигрыше очищаются данные сессии
    if msg:
        print(msg)
        session.pop('minesweeper', None)
        return jsonify({'message': msg,
                        'upd_field': render_template('minesweeper/mineField.html', field=field)})
    
    print(f'Try to {data["interact_type"]} cell {game.selected_cell_id}')
    return jsonify({'message': '',
                    'upd_field': render_template('minesweeper/mineField.html', field=field)})


#       ПОЙМАЙ КОТА
@app.route('/catch_a_cat')
def cat_catch():
    if "catch_cat" in session:
        game = session["catch_cat"]
        return render_template('catch/catch_cat.html', field=game.transformed_matrix, title='Поймай кота!')
    session['catch_cat'] = CatCatch()
    game = session['catch_cat']
    return render_template('catch/catch_cat.html', field=game.transformed_matrix, title='Поймай кота!')


@app.route('/catch_a_cat/interact', methods=['POST'])
def cat_interact_cell():
    game = session['catch_cat']
    data = request.get_json()

    cords = list(map(int, (data['coords'].split(' '))))
    if cords == list(game.cat.cords):
        cords = None
    game_response = game.interact(cords)
    field = game_response['field']
    for x in range(11):
        add_class = ' move-lefter'
        if x % 2 == 0:
            add_class = ''
        field[x] = f'<div class="row{add_class}">{"".join(field[x])}</div>'
    field = ''.join(field)

    # При выигрыше/проигрыше очищаются данные сессии
    if game_response['status'] == 'win' or game_response['status'] == 'lose':
        session.pop('catch_cat', None)
        print(f'You {game_response['status']}')
        return jsonify({'field': field, 'status': game_response['status']})
    
    print(f'Try to fill in cell {cords}')
    print(f'Move to cell {game.cat.cords}')
    return jsonify({'field': field, 'status': game_response['status']})


# Очистка сессии
@app.route('/clear_game_session', methods=['POST'])
def clear_game_session():
    data = request.get_json()
    session.pop(data['session'], None)
    return 'success'

# Окно с играми
@app.route('/games')
def games():
    return render_template('mainfiles/games_menu.html', title='Игры')

# Дальше всякая муть с логинами и регистрациями
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('mainfiles/login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('mainfiles/login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('mainfiles/register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('mainfiles/register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            age=int(form.age.data),
            name=form.name.data,
            email=form.email.data,
        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=True)
        return redirect('/')
    return render_template('mainfiles/register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(500)
def not_date(error):
    return make_response(jsonify({'Ошибка': 'Возможно при регистрации вы использовали не \
                                  латинские буквы, недоработка скоро будет исправлена'}))


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')
