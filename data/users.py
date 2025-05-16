import datetime
import sqlalchemy
from sqlalchemy import orm
from data import db_session
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class b_a_c(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'b_a_c'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)
    Easy = sqlalchemy.Column(sqlalchemy.Integer)
    Hard = sqlalchemy.Column(sqlalchemy.Integer)


class saper(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'saper'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)
    Easy = sqlalchemy.Column(sqlalchemy.Integer)
    Medium = sqlalchemy.Column(sqlalchemy.Integer)
    Hard = sqlalchemy.Column(sqlalchemy.Integer)


class cat(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'cat'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)
    rating = sqlalchemy.Column(sqlalchemy.Integer)


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True   )
    email = sqlalchemy.Column(sqlalchemy.String, 
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, 
                                      default=datetime.datetime.now, nullable=True)
    
    b_a_c_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('b_a_c.id'))
    saper_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('saper.id'))
    cat_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('cat.id'))

    b_a_c = orm.relationship('b_a_c', backref='user')
    saper = orm.relationship('saper', backref='user')
    cat = orm.relationship('cat', backref='user')

    def __repr__(self):
        return f'<User> {self.id} {self.surname} {self.name}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def create_rating(self):
        self.cat = cat(rating=0)
        db_session.session.add(self.cat)
        self.cat_id = self.cat.id
        
        self.b_a_c = b_a_c(Easy=0, Hard=0)
        db_session.session.add(self.b_a_c)
        self.b_a_c_id = self.b_a_c.id
        
        self.saper = saper(Easy=0, Medium=0, Hard=0)
        db_session.session.add(self.saper)
        self.saper_id = self.saper.id

        db_session.session.commit()

    def update_cat_rating(self):
        self.cat.rating = (self.cat.rating or 0) + 1


    def update_b_a_c_rating(self, difficult):
        if difficult == 'Easy':
            self.b_a_c.Easy = (self.b_a_c.Easy or 0) + 1
        elif difficult == 'Hard':
            self.b_a_c.Hard = (self.b_a_c.Hard or 0) + 1


    def update_saper_rating(self, difficult):
        if difficult == 'Easy':
            self.saper.Easy = (self.saper.Easy or 0) + 1
        elif difficult == 'Medium':
            self.saper.Medium = (self.saper.Medium or 0) + 1
        elif difficult == 'Hard':
            self.saper.Hard = (self.saper.Hard or 0) + 1
