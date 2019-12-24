# Importing the libraries

import json
import os
from flask import Flask, render_template, request, redirect, send_from_directory
import numpy as np
import tensorflow as tf
from db_admin import db_check
import psycopg2
from psycopg2 import sql

with open('/etc/config.json') as config_file:
    config = json.load(config_file)
db_username = config.get('DB_USERNAME')
db_password = config.get('DB_PASSWORD')

db_check()

app = Flask(__name__)

# Establishing the two folders
dir_path = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'

# Import the model H5 file
cnn_model = tf.keras.models.load_model(STATIC_FOLDER + '/' + 'catdog_classifier_Xception.h5')

IMAGE_SIZE = 224

# We preprocess the image
def preprocess_image(image):
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [IMAGE_SIZE, IMAGE_SIZE])
    # We normalize the image
    image /= 255.0

    return image

# Picking up the image from preprocessing
def load_and_preprocess_image(path):
    image = tf.io.read_file(path)
    return preprocess_image(image)

# Prediction and then labeling
def categorise(model, image_path):

    preprocessed_imgage = load_and_preprocess_image(image_path)
    preprocessed_imgage = tf.reshape(preprocessed_imgage, (1,IMAGE_SIZE ,IMAGE_SIZE ,3))

    prob = cnn_model.predict(preprocessed_imgage)
    label = "Cat" if prob >= 0.5 else "Dog"
    classified_prob = prob if prob >= 0.5 else 1 - prob
    
    return label, classified_prob

# Serving the index page
@app.route('/')
def index():
    conn = psycopg2.connect("dbname=cat_dog_checker user=" + db_username + " password=" + db_password)
    cur = conn.cursor()
    cur.execute('SELECT * FROM uploads_table ORDER BY created_at DESC LIMIT 10;')
    predictions = cur.fetchall()

    return render_template('index.html', predictions=predictions)

@app.route('/categorise', methods=['POST','GET'])
def upload_file():

    if request.method == 'GET':
        return render_template('index.html')

    else:
        file = request.files["image"]
        upload_image_path = os.path.join(UPLOAD_FOLDER, file.filename)
        print(upload_image_path)
        file.save(upload_image_path)

        label, prob = categorise(cnn_model, upload_image_path)

        prob = round((prob[0][0] * 100), 2)

        return render_template('categorise.html', image_file_name = file.filename, label = label, prob = prob)


@app.route('/feedback/<file_name>/<label>/<confidence>/<correct>/', methods=['GET'])
def save_feedback(file_name, label, confidence, correct):

    conn = psycopg2.connect("dbname=cat_dog_checker user=" + db_username + " password=" + db_password)
    cur = conn.cursor()

    query = f"""
    INSERT INTO uploads_table (file_name, label, confidence, correct) 
    VALUES (%s, %s, %s, %s);
    """

    val = (file_name, label, confidence, correct)

    cur.execute(query, val)
    conn.commit()

    cur.close()

    return redirect("/", code = 302)


@app.route('/categorise/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
    app.debug = True