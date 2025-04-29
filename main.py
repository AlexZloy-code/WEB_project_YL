import datetime
from saper_web import Minesweeper, DiffButton
from flask import Flask, render_template, redirect, request, jsonify, render_template_string, session
from data import db_session
from data.users import User
from forms.user import LoginForm, RegisterForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['SECRET_KEY'] = 'а че писать сюда'
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
    return render_template("base.html", title='Главная')

# Обработка игры
@app.route('/minesweeper')
def minesweeper():
    
    return render_template('minesweeper.html', start=True, field=[], title='Сапер')

@app.route('/minesweeper/start', methods=['POST'])
def start_game():
    data = request.get_json()
    # временная утановка: при перезагрузке вся игра слетает:
    session.pop('minesweeper', None)
    if "minesweeper" not in session:
        session["minesweeper"] = Minesweeper(data['field'])  # Создаём игру один раз для сессии
    game = session["minesweeper"]
    return jsonify({'field': render_template('minesweeper.html', field=game.matrix, title='Сапер')})


@app.route('/minesweeper/select-cell', methods=['POST'])
def select_cell():
    game = session['minesweeper']
    data = request.get_json()
    cell_id = x, y = list(map(int, data['id_cell'].split('-')))
    game.selected_cell_id = cell_id
    print(cell_id)
    return jsonify({'id_cell': str(cell_id),
                    'cell_type': game.matrix[y][x].type})


@app.route('/minesweeper/iteract', methods=['POST'])
def iteract_cell():
    game = session['minesweeper']
    x, y = game.selected_cell_id
    data = request.get_json()
    
    if data['iteract_type'] == 'flag':
        game.matrix[y][x].value = '⚐'
        if game.matrix[y][x].type == 'flaged':
            game.matrix[y][x].type = 'closed'
            game.matrix[y][x].value = ''
        else:
            game.matrix[y][x].type = 'flaged'
    else:
        game.matrix[y][x].type = 'opened'
    print(f'Try to {data['iteract_type']} cell {game.selected_cell_id}')
    return jsonify({'message': f'Try to {data['iteract_type']} cell {game.selected_cell_id}',
                    'upd_field': render_template('mineField.html', field=game.matrix)})


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
            position=form.position.data,
            speciality=form.speciality.data,
            name=form.name.data,
            email=form.email.data,
            address=form.address.data
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


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')