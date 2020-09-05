'''
Created on August 25, 2025

@author: pritam
'''

from flask import Flask, flash, render_template, redirect, url_for, request, session
from module.database import Database
import pickle
import numpy as np
import logging
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt


app = Flask(__name__)
app.secret_key = "mys3cr3tk3y"
db = Database()

def load_model():
    global model
    with open('diabetes.pkl', 'rb') as f:
        model = pickle.load(f)

@app.route('/predict_diabetes', methods=['POST'])
def predict_diabetes():
    if request.method == 'POST' and request.form['diabetes_check']:
        
        pregnancy = int(request.form.get('pregnancy'))
        plasma = int(request.form.get('plasma'))
        blood_pressure = int(request.form.get('blood_pressure'))
        skin = int(request.form.get('skin'))
        test = int(request.form.get('test'))
        pedi = float(request.form.get('pedi'))
        mass = float(request.form.get('mass'))
        age = int(request.form.get('age'))

        data = [pregnancy, plasma, blood_pressure, skin, test, pedi, mass, age]

        logging.warning(data)
        data = np.array(data)[np.newaxis, :]
        prediction = model.predict(data)
        logging.warning('Predicted Result')
        logging.warning(prediction)

    if prediction[0] == 1:
        logging.warning('You have Diabetes, please consult a Doctor.')
        flash('You have Diabetes, please consult a Doctor.')
    else:
        logging.warning('Congratulation... You do not have Diabetes. Please take care your health')
        flash('Congratulation... You do not have Diabetes. Please take care your health.')

    return redirect(url_for('diabetes'))

@app.route('/')
def index():
    data = db.read(None)

    return render_template('index.html', data = data)

@app.route('/add/')
def add():
    return render_template('add.html')

@app.route('/diabetes/')
def diabetes():
    return render_template('diabetes.html')

@app.route('/addphone', methods = ['POST', 'GET'])
def addphone():
    if request.method == 'POST' and request.form['save']:
        if db.insert(request.form):
            flash("A new patient details has been added")
        else:
            flash("A new patient details can not be added")

        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/update/<int:id>/')
def update(id):
    data = db.read(id);

    if len(data) == 0:
        return redirect(url_for('index'))
    else:
        session['update'] = id
        return render_template('update.html', data = data)

@app.route('/updatephone', methods = ['POST'])
def updatephone():
    if request.method == 'POST' and request.form['update']:

        if db.update(session['update'], request.form):
            flash('A phone number has been updated')

        else:
            flash('A phone number can not be updated')

        session.pop('update', None)

        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/delete/<int:id>/')
def delete(id):
    data = db.read(id);

    if len(data) == 0:
        return redirect(url_for('index'))
    else:
        session['delete'] = id
        return render_template('delete.html', data = data)

@app.route('/deletephone', methods = ['POST'])
def deletephone():
    if request.method == 'POST' and request.form['delete']:

        if db.delete(session['delete']):
            flash('A phone number has been deleted')

        else:
            flash('A phone number can not be deleted')

        session.pop('delete', None)

        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html')

if __name__ == '__main__':
    load_model()
    app.run(port=8181, host="0.0.0.0")
