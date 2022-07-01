from __future__ import division, print_function
from enum import unique
from inspect import currentframe
# coding=utf-8
import sys
import os
import glob, random
import re
from turtle import home
from attr import validate
from nbformat import current_nbformat
import numpy as np
from sqlalchemy import func

# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image

# Flask utils
from flask import redirect, url_for, request, render_template,flash, send_file
from flaskAtlas import app,db,bcrypt
from flaskAtlas.forms import RegistrationForm, LoginForm
from flaskAtlas.models import User,Image
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename

from io import BytesIO

# Paths for images datasets
SITTING_PATH = r'C:\Users\camra\env\AtlasP\flaskAtlas\static\Gallery\Sitting'
WITHAPET_PATH = r'C:\Users\camra\env\AtlasP\flaskAtlas\static\Gallery\WithAPet'
CLOSESHOT_PATH = r'C:\Users\camra\env\AtlasP\flaskAtlas\static\Gallery\CloseShot'


# Model saved with Keras model.save()
MODEL_PATH =r'C:\Users\camra\env\Final project\Artstyles.h5'
MODEL_PATH2 =r'C:\Users\camra\env\Final project\Poses.h5'

# Load your trained model
model = load_model(MODEL_PATH)
model2 = load_model(MODEL_PATH2)



def model_predict(img_path, model):
    print(img_path)
    img = image.load_img(img_path, target_size=(224, 224))

    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="Anime"
    elif preds==1:
        preds="Comic"
    elif preds==2:
        preds="Semi_realism"
    return preds


def model_predict2(img_path, model):
    print(img_path)
    img = image.load_img(img_path, target_size=(224, 224))

    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="Close shot"
    elif preds==1:
        preds="Sitting"
    elif preds==2:
        preds="With a pet"
    return preds


def random_img(file_path_type):
    #print("done till here")
    print(file_path_type)
    images = glob.glob(file_path_type)
    #print("solved")
    print(images)
    random_image = random.choice(images)
    #print("problem here")
    print(random_image)
    return random_image


@app.route("/")
@app.route("/index", methods=['GET', 'POST'])
@login_required
def index():
    if (request.method == 'POST'):

        # Count_test = Image.query.filter_by(pose = 'With a pet', user_id = current_user.id).count()
     
        # CountC = db.session.query(Image, func.count(Image.pose)).filter(Image.pose == 'Close shot', Image.user_id== current_user.id).all()
        # CountC = db.select([func.count(Image.pose)]).where(db.and_(Image.pose == 'Close shot', Image.user_id == current_user.id ))
        # CountS = db.select([func.count(Image.pose)]).where(db.and_(Image.pose == 'Sitting', Image.user_id == current_user.id ))
        # CountS = db.session.query(Image, func.count(Image.pose)).filter(Image.pose == 'Sitting', Image.user_id == current_user.id).all()
        # CountW = db.select([func.count(Image.pose)]).where(db.and_(Image.pose == 'With a pet', Image.user_id == current_user.id ))
        CountC = Image.query.filter_by(pose = 'Close shot', user_id = current_user.id).count()
        CountS = Image.query.filter_by(pose = 'Setting', user_id = current_user.id).count()
        CountW = Image.query.filter_by(pose = 'With a pet', user_id = current_user.id).count()

        #print(f'count c = {CountC} and s  = {CountS} and final = {CountW}')
        least = min(CountC,CountS,CountW)
        #print("done ")
        basdir = os.path.abspath(os.path.dirname(__file__))
        basdir = basdir + "\\static\\Gallery\\"


        if(least==CountC):
            file_path_type =basdir + "CloseShot\\*.jpg"
        elif(least==CountS):
            file_path_type = basdir + "Sitting\\*.jpg"
        else:
            file_path_type = basdir + "WithAPet\\*.jpg"
        #print("dont")

        random_image1= random_img(file_path_type)
        random_image2= random_img(file_path_type)
        random_image3= random_img(file_path_type)
        #print(random_image1)
        #random_image1 = basdir + "\\static\\Gallery\\Sitting\\Sitting.jpg"
        # C:\Users\camra\env\AtlasP\flaskAtlas\static\Gallery\Sitting
        # C:\Users\camra\env\AtlasP\flaskAtlas/static/Gallery//Sitting\Sitting (7).jpg

        return render_template('index.html',random_image1=random_image1,random_image2=random_image2,random_image3=random_image3)

    return render_template('index.html')


@app.route("/YourExhibit", methods=['GET'])
@login_required
def YourExhibit():
    Idata = Image.query.filter_by(user_id=current_user.id).all()
    return render_template('YourExhibit.html',title='YourExhibit',images=Idata)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form= RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form= LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember =form.remember.data )
            next_page= request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route("/image_upload", methods=['GET'])
@login_required
def image_upload():
    return render_template('image_upload.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)

        file_path = os.path.join(
            basepath, 'static/uploads', secure_filename(f.filename))

        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)
        preds2 = model_predict2(file_path, model2)
        result=preds+' '+preds2

        # Save the file to database
        upload = Image(imageName=f.filename, data=f.read(),pose=preds2 , style=preds, auther=current_user)
        db.session.add(upload)
        db.session.commit()

        return result
    return None




    
    