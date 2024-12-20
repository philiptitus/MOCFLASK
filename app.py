from flask import Flask, request, jsonify
from utils import gen_cases, create_db # added the import for create_db function
import sqlalchemy

app = Flask(__name__)

@app.route('/generate_cases', methods=['POST'])
def generate_cases():
    try:
        data = request.get_json()  # Get JSON data from request

        language = data.get('language')
        sex = data.get('sex')
        age = data.get('age')

        if not all([language, sex, age]):
            return jsonify({"error": "language, sex, and age are required fields."}), 400

        try:
            age = int(age)
        except (TypeError, ValueError):
            return jsonify({"error": "age must be a valid integer."}), 400
          
        engine = sqlalchemy.create_engine('sqlite:///./cases.db')
        create_db(engine) # create database if it doesn't exist

        try:
  
            
            
            
            gen_cases(language, sex, age)  # Call your utility function
            return jsonify({"message": "Cases generated successfully."}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
