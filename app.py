from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, URL, NumberRange
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///adopt'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)

class Pet(db.Model):
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    species = db.Column(db.String, nullable=False)
    photo_url = db.Column(db.String, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    available = db.Column(db.Boolean, default=True, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def homepage():
    pets = Pet.query.all()
    return render_template('homepage.html', pets=pets)

class PetForm(FlaskForm):
    name = StringField('Pet Name', validators=[DataRequired()])
    species = StringField('Species', validators=[DataRequired()])
    photo_url = StringField('Photo URL', validators=[Optional(), URL()])
    age = IntegerField('Age', validators=[Optional(), NumberRange(min=0, max=30)])
    notes = TextAreaField('Notes', validators=[Optional()])
    available = BooleanField('Available', default=True)
    submit = SubmitField('Submit')


@app.route('/add', methods=['GET', 'POST'])
def add_pet():
    form = PetForm()
    if form.validate_on_submit():
        new_pet = Pet(
            name=form.name.data,
            species=form.species.data,
            photo_url=form.photo_url.data,
            age=form.age.data,
            notes=form.notes.data,
            available=form.available.data
        )
        db.session.add(new_pet)
        db.session.commit()
        return redirect('/')
    return render_template('add_pet.html', form=form)

@app.route('/<int:pet_id>')
def pet_detail(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template('pet_detail.html', pet=pet)

@app.route('/<int:pet_id>', methods=['POST'])
def edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    form = PetForm()
    if form.validate_on_submit():
        pet.photo_url = form.photo_url.data
        pet.notes = form.notes.data
        pet.available = form.available.data
        db.session.commit()
        return redirect('/')
    return render_template('pet_detail.html', pet=pet, form=form)

if __name__ == "__main__":
    app.run(debug=True)