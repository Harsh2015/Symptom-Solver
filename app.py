from flask import Flask, render_template, request, redirect, flash, url_for, session, jsonify
from flask_mysqldb import MySQL
import bcrypt
from flask_sqlalchemy import SQLAlchemy
import pickle
import numpy as np
import pandas as pd
from fuzzywuzzy import process
from antibiotic import antibiotic_data
from encoding import *
import json
import requests
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = '32327dh3hb4h5bh3b4'

#####################  MySQL database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'symptom-solver'

######## Initializing MySQL and SQLAlchemy for database operations
mysql = MySQL(app)
db = SQLAlchemy()
CORS(app)

# Loading a pre-trained Decision Tree (DT) model using pickle
with open(r"C:\Users\HARSH\Desktop\SymptomSolver\d_model.pkl", 'rb') as model_file:
    model = pickle.load(model_file)

# Rendering the home page template
@app.route('/')
def home():
    return render_template('symptom-solver.html')


# Rendering the about page template
@app.route('/about')
def about():
    return render_template('about.html')

from flask import flash, redirect, render_template, request, url_for

# Handle user login functionality
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

         # Fetch user details from the database based on the provided email
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT email, password_hash, username FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            db_email, db_password_hash, db_name = user

            # Check if the entered password matches the stored password hash
            if bcrypt.checkpw(password.encode('utf-8'), db_password_hash.encode('utf-8')):

                # On successful login, store user details in the session
                session['user_email'] = db_email
                session['user_name'] = db_name
                flash('Logout successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials, please try again.', 'error')  # Incorrect password message
        else:
            flash('Invalid credentials, please try again.', 'error')     # User not found message

    return render_template('login.html')

# Render the user profile page
@app.route('/user-profile', methods=['GET'])
def profile():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    # Get the email from session to fetch user data
    user_email = session['user_email']
    
    # Get user data from database based on session email
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username, email, age, location FROM users WHERE email = %s", (user_email,))
    user_data = cursor.fetchone()
    cursor.close()

    if user_data:
        username, email, age, location = user_data
        return render_template('profile.html', username=username, email=email, age=age, location=location)
    else:
        flash('User data not found', 'error')
        return redirect(url_for('login'))

# Route to update user profile information like age and location
@app.route('/update-profile', methods=['POST'])
def update_profile():
    # Check if the user is logged in by verifying the session
    if 'user_email' not in session:
        return redirect(url_for('login')) 
    
    user_email = session['user_email']
    data = request.get_json()
    
    # Extract age and location from the JSON data
    age = data['age']
    location = data['location']

    # Try updating the user's profile in the database
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE users SET age = %s, location = %s WHERE email = %s",
            (age, location, user_email)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({'status': 'success', 'message': 'Profile updated successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Route to handle user signup 
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))

        # Hash the password using bcrypt for security
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Try saving the user data in the database
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO users (email, username, password_hash) VALUES (%s, %s, %s)", 
                           (email, username, hashed_password))
            mysql.connection.commit()
            cursor.close()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:

            # If an error occurs, display it to the user
            flash('An error occurred: ' + str(e), 'danger')
            return redirect(url_for('signup'))

    return render_template('signup.html')

# Route to display the dashboard, accessible only to logged-in users
@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        flash('Please log in to access the dashboard.', 'info')
        return redirect(url_for('login'))
    return render_template('dashboard.html')


# Function to encode symptom using fuzzy matching for better accuracy
def encode_symptom(symptom, column):
    # Fetch the symptom-to-encoded value dictionary for the respective column
    symptom_dict = symptom_to_encoded.get(column, {})
    match = process.extractOne(symptom, symptom_dict.keys())
    if match and match[1] > 80:
        return symptom_dict[match[0]]
    else:
        print(f"Unknown symptom: {symptom} in column {column}")
        return 0

# Route for predicting the disease based on user symptoms
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == "POST":
        # Parse incoming JSON data
        data = request.get_json()

        # Extract symptoms from the request, defaulting to 'No Symptoms' if not provided
        symptoms = [
            data.get('symptom1', 'No Symptoms'),
            data.get('symptom2', 'No Symptoms'),
            data.get('symptom3', 'No Symptoms'),
            data.get('symptom4', 'No Symptoms'),
            data.get('symptom5', 'No Symptoms'),
            data.get('symptom6', 'No Symptoms'),
        ]

        # Encode symptoms using the encode_symptom function
        encoded_symptoms = []
        for idx, symptom in enumerate(symptoms, start=1):
            column = f's{idx}'
            encoded_value = encode_symptom(symptom, column)
            encoded_symptoms.append(encoded_value)

        # If all symptoms are invalid (encoded as 0), return an error response
        if all(value == 0 for value in encoded_symptoms):
            return jsonify({
                'disease': 'Invalid Symptoms',
                'medicines': []   # Empty list as no valid symptoms were provided
            })

        # Create a DataFrame to make a prediction
        user_input_df = pd.DataFrame([encoded_symptoms], columns=['s1', 's2', 's3', 's4', 's5', 's6'])

        try:
            # Predict the disease using the pre-trained model
            model_output = model.predict(user_input_df)[0]
            print(f"Model Output: {model_output}")  # Debug output

            # Convert model output to an integer if it's not already
            if isinstance(model_output, (np.int64, float, np.float64)):
                model_output = int(model_output)  # Convert to integer

            # Map model output to the disease name
            predicted_disease = encoded_to_disease.get(model_output, "Unknown Disease")
            print(f"Predicted Disease after mapping: {predicted_disease}")

        except Exception as e:
            print(f"Prediction error: {e}")
            predicted_disease = "Error during prediction"

        # Return prediction results along with placeholder medicines
        return jsonify({
            'disease': predicted_disease,
            'medicines': ["Medicine 1", "Medicine 2", "Medicine 3"]  # Placeholder for medicines
        })

# Route to get a list of antibiotics based on a disease name
@app.route('/get_antibiotics', methods=['POST'])
def get_antibiotics():
    disease = request.json.get('Disease')
    # Check if the disease exists in the antibiotic data dictionary
    if disease in antibiotic_data:
        return jsonify({
            'success': True,
            'data': antibiotic_data[disease]
        })
    else:
    # If the disease is not found, return an error message with a 404 status code
        return jsonify({
            'success': False,
            'error': 'Disease not found'
        }), 404

# Route to handle user logout
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Route to handle chatbot interactions
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    # Checks if the user is logged in before allowing access to the chatbot
    if 'user_email' not in session:
        flash('Please log in to access chatbot.', 'info')
        return redirect(url_for('login'))
    
  
    if request.method == 'POST':
        user_prompt = request.form.get('prompt')
        
        # If no prompt is provided, return a bad request error (400)
        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Create a template for the API request to the chatbot model
        template = {
            "model": "gemma2:2b",
            "prompt": user_prompt,
            "stream": False
        }

        try:
            # Send the POST request to the local chatbot API
            res = requests.post('http://127.0.0.1:11434/api/generate', json=template)
            llm_response = json.loads(res.text)
            return jsonify({"response": llm_response.get('response', 'No response available')})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return render_template('chat.html')




if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=5000)