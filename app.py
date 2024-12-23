from flask import Flask, render_template, url_for, send_from_directory, request, jsonify
from utils import gen_cases, create_db # added the import for create_db function
import sqlalchemy
from pathlib import Path
import json
import os
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  #For development reload the template
BASE_DIR = Path(__file__).resolve().parent


@app.route('/')  #Serve the index.html file when you go to the root path.
def serve_index():
    return render_template('index.html')



@app.route('/generate_cases', methods=['POST'])
def generate_cases():
    try:
        data = request.get_json()
        language = data.get('language')
        sex = data.get('sex')
        age = data.get('age')

        if not all([language, sex, age]):
            return jsonify({"error": "language, sex, and age are required fields."}), 400

        try:
            age = int(age)
        except (TypeError, ValueError):
            return jsonify({"error": "age must be a valid integer."}), 400

        output_dir = BASE_DIR / 'output' / 'game'  # Output directory using BASE_DIR
        output_dir.mkdir(parents=True, exist_ok=True) #Create the directory if it doesn't exist.

        try:
            generated_data = gen_cases(language, sex, age, output_dir) # Pass the output directory

            if generated_data:
                return jsonify({'data': generated_data}), 200
            else:
                return jsonify({'error': 'Failed to generate cases'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    return jsonify({"message": "Response recorded"}), 200


if __name__ == '__main__':
    app.run(debug=True)

