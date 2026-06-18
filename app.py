from flask import Flask, render_template, request, redirect, flash, url_for, session, jsonify
import pickle
import numpy as np
import pandas as pd
from fuzzywuzzy import process
from JSON_Datasets.antibiotic import antibiotic_data
from JSON_Datasets.encoding import *
import json
from JSON_Datasets.tests import tests_dict
import os

app = Flask(__name__)
app.secret_key = '32327dh3hb4h5bh3b4'

# Base project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load ML Model
model_path = os.path.join(BASE_DIR, "d_model.pkl")

with open(model_path, "rb") as model_file:
    model = pickle.load(model_file)

# Load Diet Recommendations JSON
diet_json_path = os.path.join(
    BASE_DIR,
    "JSON_Datasets",
    "diet_recommendations.json"
)

with open(diet_json_path, "r", encoding="utf-8") as file:
    diet_data = json.load(file)

# Rendering the home page template
@app.route('/')
def home():
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

    
@app.route('/get_diseases', methods=['GET'])
def get_diseases():
    """Returns a list of all available diseases."""
    diseases = list(set(tests_dict.keys()) | set(diet_data.keys()))  # Merge diseases from both sources
    return jsonify({'diseases': diseases})

@app.route('/get_tests', methods=['POST'])
def get_tests():
    """Returns test details, outcomes, and diet/lifestyle recommendations."""
    data = request.get_json()
    disease = data.get("Disease")

    if not disease:
        return jsonify({"error": "No disease provided"}), 400

    # Fetch test details from tests.py
    disease_info = tests_dict.get(disease, {})
    tests = disease_info.get("tests", [])
    outcome = disease_info.get("outcome", "No outcome available.")
    definition = disease_info.get("definition", {})

    # Ensure test definition are available
    test_definitions = {test: definition.get(test, "No definition available.") for test in tests}

    # Fetch diet & lifestyle recommendations from JSON
    recommendations = diet_data.get(disease, {
        "foods_to_eat": [],
        "foods_to_avoid": [],
        "lifestyle_tips": []
    })

    return jsonify({
        "tests": tests,
        "outcome": outcome,
        "definition": definition,
        "recommendations": recommendations
    })


@app.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    disease = request.args.get('disease')
    if not disease:
        return jsonify({"error": "Please provide a disease name"}), 400
    
    recommendations = diet_data.get(disease)
    if not recommendations:
        return jsonify({"error": "No recommendations found for this disease"}), 404
    
    return jsonify(recommendations)




if __name__ == '__main__':
  app.run(debug=False, host='0.0.0.0', port=5000)