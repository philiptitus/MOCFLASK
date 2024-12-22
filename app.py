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
    try:
        data = request.get_json()
        answers = data.get('answers')

        if not answers:
            return jsonify({"error": "Answers are required."}), 400

        json_file_path = BASE_DIR / 'output' / 'game' / "option_1.json" # Using BASE_DIR
        if not json_file_path.exists():
            return jsonify({"error": "No cases found."}), 404

        with open(json_file_path, 'r') as f:
            cases_data = json.load(f)

        total_score = 0
        max_total_score = 0
        results = []

        # Check if all cases are answered
        if len(answers) != len(cases_data['cases']):
            return jsonify({"error": "Please answer all cases."}), 400


        for case_data in cases_data['cases']:
            case_id = case_data['case_id']
            user_answer = next((answer for answer in answers if answer['case_id'] == case_id), None)

            if not user_answer:
                return jsonify({"error": f"Answer for case {case_id} not found."}), 400

            option_id = user_answer['option_id']
            selected_option = next((option for option in case_data['options'] if option['option_id'] == option_id), None)

            if not selected_option:
                return jsonify({"error": f"Invalid option ID {option_id} for case {case_id}."}), 400

            # Calculate score for the case
            total_option_score = sum([selected_option[attr] for attr in ['health', 'wealth', 'relationships', 'happiness', 'knowledge', 'karma', 'time_management', 'environmental_impact', 'personal_growth', 'social_responsibility']])
            optimal_option = next((option for option in case_data['options'] if option['number'] == case_data['optimal']), None)
            max_option_score = sum([optimal_option[attr] for attr in ['health', 'wealth', 'relationships', 'happiness', 'knowledge', 'karma', 'time_management', 'environmental_impact', 'personal_growth', 'social_responsibility']])

            case_score = total_option_score
            max_case_score = max_option_score

            total_score += case_score
            max_total_score += max_case_score
            results.append({
                'case_id': case_id,
                'score': case_score,
                'max_score': max_case_score
            })


        #Delete the file after successful processing
        os.remove(json_file_path)

        return jsonify({
            'results': results,
            'total_score': total_score,
            'max_total_score': max_total_score
        }), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500




if __name__ == '__main__':
    app.run(debug=True)

