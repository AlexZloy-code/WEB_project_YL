import datetime

from flask import Flask, render_template, redirect, request, jsonify, make_response, session
from data import db_session
from data.users import User
from forms.user import LoginForm, RegisterForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session

from saper_web import Minesweeper
from bullsCows import BullsCows

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
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
    return render_template("index.html", title='Главная')

#          САПЕР
@app.route('/minesweeper')
def minesweeper():
    if "minesweeper" in session:
        game = session["minesweeper"]
        return render_template('minesweeper.html', field=game.transformed_matrix, title='Сапер')
    return render_template('minesweeper.html', start=True, field=[], title='Сапер')

@app.route('/minesweeper/start', methods=['POST'])
def start_game():
    data = request.get_json()

    if "minesweeper" not in session:
        session["minesweeper"] = Minesweeper(data['field'])  # Создаём игру один раз для сессии
    game = session["minesweeper"]

    return jsonify({'field': render_template('minesweeper.html', field=game.transformed_matrix, title='Сапер')})


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
                        'upd_field': render_template('mineField.html', field=field)})
    
    print(f'Try to {data['interact_type']} cell {game.selected_cell_id}')
    return jsonify({'message': '',
                    'upd_field': render_template('mineField.html', field=field)})


#   БЫКИ И КОРОВЫ
@app.route('/bulls_and_cows')
def bulls_and_cows():
    if 'bulls_and_cows' not in session:
        session['bulls_and_cows'] = BullsCows()
    game = session['bulls_and_cows']

    return render_template('bulls_and_cows.html', title='Быки и коровы',
                           history=list(map(lambda x: x.replace('<br>', '\n'), game.history)))

@app.route('/bulls_and_cows/make_guess', methods=['POST'])
def make_guess():
    game = session['bulls_and_cows']
    data = request.get_json()
    guess = game.make_guess(data['number'])
    if guess['status'] == 'win':
        session.pop('bulls_and_cows', None)
    if guess['status'] == 'error':
        return jsonify({'response': guess['message'], 'status': guess['status']})
    return jsonify({'response': '<br>'.join(guess['message'][::-1]),
                    'status': guess['status']})


# Очистка сессии
@app.route('/clear_game_session', methods=['POST'])
def clear_game_session():
    data = request.get_json()
    session.pop(data['session'], None)
    return 'success'


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
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
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
    return render_template('register.html', title='Регистрация', form=form)


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