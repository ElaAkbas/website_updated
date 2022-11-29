from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from werkzeug.utils import secure_filename
from transformers import BeitFeatureExtractor, BeitForImageClassification
from PIL import Image
import bcrypt, pyodbc
import pylab
import requests
import os
import wave
import numpy as np

app = Flask(__name__, template_folder='template', static_folder='template/static')
app.config['SESSION_TYPE'] = 'filesystem'
images_folder_path = "template/static/images"
sounds_folder_path = "template/static/sounds"
app.config['UPLOAD_IMAGE_FOLDER'] = images_folder_path
app.config['UPLOAD_SOUND_FOLDER'] = sounds_folder_path
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
Session(app)

def graph_spectrogram(wav_file):
    sound_info, frame_rate = get_wav_info(wav_file)
    pylab.figure(num=None, figsize=(19, 12))
    pylab.subplot(111)

    pylab.specgram(sound_info, Fs=frame_rate)
    pylab.savefig('spectrogram.jpg')


def get_wav_info(wav_file):
    wav = wave.open(wav_file, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate


def predict(file):
    file_name = os.path.split(file)[-1]

    if file_name[-3:] != "wav":
        image = Image.open(file)
        feature_extractor = BeitFeatureExtractor.from_pretrained('microsoft/beit-base-patch16-224-pt22k-ft22k')
        model = BeitForImageClassification.from_pretrained('microsoft/beit-base-patch16-224-pt22k-ft22k')
        inputs = feature_extractor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits
        # model predicts one of the 21,841 ImageNet-22k classes
        predicted_class_idx = logits.argmax(-1).item()
        result = model.config.id2label[predicted_class_idx].split(",")[0]
        # print("Predicted class:", result)
        return result
    else:
        graph_spectrogram(file)
        image = Image.open("spectrogram.jpg")
        feature_extractor = BeitFeatureExtractor.from_pretrained('microsoft/beit-base-patch16-224-pt22k-ft22k')
        model = BeitForImageClassification.from_pretrained('microsoft/beit-base-patch16-224-pt22k-ft22k')
        inputs = feature_extractor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits
        # model predicts one of the 21,841 ImageNet-22k classes
        predicted_class_idx = logits.argmax(-1).item()
        # since i saved the spectrogram file in the same dir i am deleting it here prob have do edit this depending where and how we run the code
        # os.remove("spectrogram.jpg")
        result = model.config.id2label[predicted_class_idx].split(",")[0]
        # print("Predicted class:", result)
        return result


def connection(query, getResult=True):
    s = 'DESKTOP-7R8HL94\SQLEXPRESS'
    d = 'website'
    u = 'Ela'
    p = '123'
    cstr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + s + ';DATABASE=' + d + ';UID=' + u + ';PWD=' + p
    conn = pyodbc.connect(cstr)
    print('CONNECTED!')
    cursor = conn.cursor()
    print(query)
    cursor.execute(query)
    if getResult:
        result = cursor.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result


def Encrypt(p):
    # Got the bcrypt idea from this youtube video https://www.youtube.com/watch?v=CSHx6eCkmv0
    passwd = bytes(p, encoding='UTF-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwd, salt)
    hashed = hashed.decode(encoding='UTF-8')
    return hashed


def check_password(password, email):
    passwd = bytes(password, encoding='UTF-8')
    hashed = connection(f"select password from customer where email = '{email}'", getResult=True)
    hashed = bytes(hashed[0][0], encoding='UTF-8')
    if bcrypt.checkpw(passwd, hashed):
        return True
    else:
        return False

def spaces_start_end(string):
    for count, letter in enumerate(string):
        if letter == ' ':
            continue
        else:
            string = string[count:]
            break
    count = 0
    for letter in string[::-1]:
        if letter == ' ':
            count = count - 1
        else:
            if count == 0:
                break
            string = string[:count]
            break
    return string


def spaces_mid(string):
    result = False
    for letter in string:
        if letter == ' ':
            result = True
            break
    return result


def allowed_image_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_sound_file(filename):
    ALLOWED_EXTENSIONS = {'wav'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    prediction_image = None
    prediction_sound = None
    image_upload = 'images/default_images/animals.png'
    if request.method == 'POST':

        if "Back" in request.form:
            return redirect(url_for('index12'))

        image = request.files["image"]
        sound = request.files["sound"]
        if 'customer_id' in session:
            if image.filename == '' and sound.filename == '':

                flash("You did not select any files")
            if image.filename != '':
                if allowed_image_file(secure_filename(image.filename)):
                    image_folder_path = app.config['UPLOAD_IMAGE_FOLDER'] + '/' + str(session['customer_id'])
                    if not os.path.exists(image_folder_path):
                        os.makedirs(image_folder_path)
                    img_path = os.path.join(image_folder_path, secure_filename(image.filename))
                    image.save(img_path)
                    prediction_image = predict(img_path) #do we use img_path or image.filename?
                    image_filename = secure_filename(image.filename)
                    image_upload = 'images/' +  str(session['customer_id']) + '/' + image_filename
                    flash('Your image is successfully uploaded')
                else:
                    flash('Please upload an image with the file extension png, jpg or jpeg')
            if sound.filename != '':
                if allowed_sound_file(secure_filename(sound.filename)):
                    sound_folder_path = app.config['UPLOAD_SOUND_FOLDER'] + '/' + str(session['customer_id'])
                    if not os.path.exists(sound_path):
                        os.makedirs(sound_path)
                    sound_path = os.path.join(sound_folder_path, secure_filename(sound.filename))
                    sound.save(sound_path)
                    prediction_sound = predict(sound_path)
                    flash('Your sound file is successfully uploaded')
                else:
                    flash('Please upload a sound file with the file extension wav')
        else:
            flash('You are not logged in yet. Log in or create an account to upload a file for the prediction.')
            return redirect(url_for('login'))
    if not prediction_image:
        prediction_image = None
    if not prediction_sound:
        prediction_sound = None
    return render_template('upload_new.html', prediction_image = prediction_image, prediction_sound = prediction_sound, image_upload = image_upload)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        if "Back" in request.form:
            return redirect(url_for('index12'))
        # print(request.form)
        feedback_score = request.form['rating']
        feedback = 'No'
        # print(feedback_score)

        if "email" in session:
            email = session['email']
            if "subject" in request.form:
                feedback = request.form["subject"]
            get_customer_id = connection(f"select id from customer where email = '{email}'", getResult=True)
            get_account_id = connection(f"select id from account where customer_id = '{get_customer_id[0][0]}'",
                                        getResult=True)
            connection(f"insert into feedback(account_id, feedback_button, feedback_text, issue, solved_by)"
                       f"values('{get_account_id[0][0]}', '{feedback_score}', '{feedback}', null, null)",
                       getResult=False)
        else:
            flash('You are not logged in. Login or create account to give feedback.')
            return redirect(url_for('login'))
        flash('Thank you, your feedback is successfully submitted.')
        return redirect(url_for('index12'))
    return render_template('contact.html')


@app.route('/account', methods=['GET', 'POST'])
def createaccount():
    if request.method == "POST":
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        age = request.form["age"]
        email = request.form["email"]
        email = spaces_start_end(email)
        password = request.form["psw"]
        new_password_1 = request.form["psw-repeat"]
        gender = request.form['gender']

        if 'create' in request.form:
            try:
                string_age = int(age)
                print(string_age)
            except ValueError:
                flash('Invalid age. Insert digits only, please.')
            if first_name == '' or last_name == '' or age == '' or email == '' or password == '' or new_password_1 == '':
                flash('One or more fields are empty')
            elif spaces_mid(email):
                flash('There are space(s) in your email address')
            elif new_password_1 == password:
                encripted_pw = Encrypt(new_password_1)
                email_already_exists = connection(f"select * from customer where email = '{email}'", getResult=True)
                if not email_already_exists:
                    connection(
                        f"insert into customer(first_name, last_name, password, age, email, gender) values('{first_name}', '{last_name}', '{encripted_pw}', '{age}', '{email}','{gender}')",
                        getResult=False)
                    get_id = connection(f'select * from customer', getResult=True)
                    connection(
                        f"insert into account(employee_id, customer_id, islogin, lastupdated, lastupdatedreason, lastupdatedby, prediction) values(null, '{get_id[-1][0]}', null, null, null, null, null)",
                        getResult=False)
                    flash('Your account is successfully created, you can login!')
                    return redirect(url_for('login'))
                elif email_already_exists:
                    flash('An account with this email address already exists.')
                    return redirect(url_for('login'))
            else:
                flash('The repeated password is not the same as the first one. Try again.')
        if 'cancel' in request.form:
            return redirect(url_for('login'))
    return render_template('createaccount.html')


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == "POST":
        user_email = request.form["enter email"]
        user_email = spaces_start_end(user_email)
        password_forgot = request.form["new password"]
        repeat_new_pw = request.form["repeat new password"]
        check_email_exists = connection(f"select email from customer where email = '{user_email}'", getResult=True)
        if 'save' in request.form:
            if user_email == '' or password_forgot == '' or repeat_new_pw == '':
                flash('One or more fields are empty')
            elif 'email' in session:
                flash('You are already logged in')
                return redirect(url_for('index12'))
            elif not check_email_exists:
                flash('Email does not exist')
                return redirect(url_for('forgot'))
            elif check_email_exists and password_forgot == repeat_new_pw:
                encripted_new_pw = Encrypt(repeat_new_pw)
                connection(f"update customer set password = '{encripted_new_pw}' where email = '{user_email}'",
                           getResult=False)  # uncomment this when deploying
                flash('Password successfully changed, you can login')
                return redirect(url_for('login'))
            elif password_forgot != repeat_new_pw:
                flash('Passwords do not match')
                return redirect(url_for('forgot'))
        if "cancel_forgot" in request.form:
            return redirect(url_for('login'))
    return render_template('forgot.html')


@app.route('/library', methods=['GET', 'POST'])
def library():
    if "Back" in request.form:
        return redirect(url_for('index12'))
    image1 = '/images/default_images/Wild_aye_aye_lumar.jpg'
    image2 = '/images/default_images/Thorny_Dragon.jpg'
    image3 = '/images/default_images/Saiga_Antelope.jpg'
    image4 = '/images/default_images/Proboscis_Monkey.jpg'
    image5 = '/images/default_images/Sunda_Colugo.jpg'
    image6 = '/images/default_images/Fossa.jpg'
    return render_template('library.html' , image1 = image1, image2 = image2, image3 = image3, image4 = image4, image5 = image5, image6 = image6)


@app.route('/home', methods=['GET', 'POST'])
def index12():
    if request.method == "POST":

        if request.form.get("library") == "Library":
            return redirect(url_for('library'))

        elif request.form.get("upload_new") == "Upload":
            return redirect(url_for('upload'))

        elif request.form.get("contact") == "Contact Us":
            return redirect(url_for('contact'))

        elif request.form.get("settings") == "Settings":
            return redirect(url_for('settings'))

        elif request.form.get("loginnew") == "Log out":
            session.clear()
            return redirect(url_for('login'))
    return render_template('index12.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        print(request.form)
        email = request.form["email"]
        email = spaces_start_end(email)
        pw = request.form["psw"]

        if "sign_in" in request.form:
            check_email = connection(f"select email from customer where email = '{email}'", getResult=True)
            if email == '' or pw == '':
                flash('One or more fields are empty')
                return redirect(url_for('login'))
            elif len(check_email) > 0:
                check_pw = check_password(pw, email)
                if check_pw == True:
                    session['email'] = email
                    customer_id = connection(f"select id from customer where email = '{email}'", getResult=True)
                    session['customer_id'] = customer_id[0][0]
                    return redirect(url_for('index12'))
                else:
                    flash('Inserted wrong password')
                    return redirect(url_for('login'))
            else:
                flash('This email address does not exist')
                return redirect(url_for('login'))
            return redirect(url_for('index12'))


        if request.form.get("forgot") == "Forgot Password":
            return redirect(url_for('forgot'))

        if request.form.get("create_account") == "Create new Account":
            return redirect(url_for('createaccount'))
    return render_template('loginnew.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == "POST":

        print(request.form)
        enter_email = request.form["enter email"]
        enter_email = spaces_start_end(enter_email)
        current_password = request.form["current password"]
        new_pw = request.form["enter new password"]
        repeat = request.form["repeat new password"]

        if 'save' in request.form:
            if 'email' not in session:
                flash('You are not logged in yet. Login to access your settings.')
                return redirect(url_for('login'))
            elif enter_email == '' or current_password == '' or new_pw == '' or repeat == '':
                flash('One or more fields are empty')
            elif session['email'] == enter_email and check_password(current_password, enter_email):
                if new_pw == repeat:
                    encripted_new_pw = Encrypt(new_pw)
                    connection(f"update customer set password = '{encripted_new_pw}' where email = '{enter_email}'",
                               getResult=False)
                    flash('Your password is successfully changed.')
                    return redirect(url_for('index12'))
                else:
                    flash('Repeated password is not the same as new password.')
            elif session['email'] != enter_email:
                flash('Email entered is not the email for this account.')
            elif not check_password(current_password, enter_email):
                flash('Inserted current password is not correct.')
        if 'cancel' in request.form:
            return redirect(url_for('index12'))
    return render_template('settings.html')


if __name__ == '__main__':
    app.run('127.0.0.1', port=8080, debug=True)  #
