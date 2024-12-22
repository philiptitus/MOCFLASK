# your_flask_app/utils.py
import sqlalchemy

import json
from pathlib import Path
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image
import ast
import google.generativeai as genai  # Import Gemini module
from dotenv import load_dotenv  # Import dotenv for loading .env file
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
# Load environment variables

import uuid  # Import uuid for unique ID generation





Base = declarative_base() #SQLAlchemy Base


#Define your SQLAlchemy models here:
class TopLevelOption(Base):
    __tablename__ = 'top_level_options'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    text = sqlalchemy.Column(sqlalchemy.String(255))
    cases = relationship("Case", backref="top_level_option")

    def __repr__(self):
        return f"<TopLevelOption(text='{self.text}')>"

class Case(Base):
    __tablename__ = 'cases'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    top_level_option_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('top_level_options.id'))
    text = sqlalchemy.Column(sqlalchemy.Text)
    optimal_option = sqlalchemy.Column(sqlalchemy.Integer)
    options = relationship("CaseOption", backref="case")

    def __repr__(self):
        return f"<Case(text='{self.text[:20]}...')>"

class CaseOption(Base):
    __tablename__ = 'case_options'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    case_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('cases.id'))
    number = sqlalchemy.Column(sqlalchemy.Integer)
    text = sqlalchemy.Column(sqlalchemy.String(255))
    health = sqlalchemy.Column(sqlalchemy.Integer)
    wealth = sqlalchemy.Column(sqlalchemy.Integer)
    relationships = sqlalchemy.Column(sqlalchemy.Integer)
    happiness = sqlalchemy.Column(sqlalchemy.Integer)
    knowledge = sqlalchemy.Column(sqlalchemy.Integer)
    karma = sqlalchemy.Column(sqlalchemy.Integer)
    time_management = sqlalchemy.Column(sqlalchemy.Integer)
    environmental_impact = sqlalchemy.Column(sqlalchemy.Integer)
    personal_growth = sqlalchemy.Column(sqlalchemy.Integer)
    social_responsibility = sqlalchemy.Column(sqlalchemy.Integer)

    def __repr__(self):
        return f"<CaseOption(text='{self.text}')>"


# Function to create the database tables
def create_db(engine):
    Base.metadata.create_all(engine)



load_dotenv()

# Load the API key from environment variables
GENAI_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GENAI_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the .env file.")
genai.configure(api_key=GENAI_API_KEY)

# Define the base directory for the Flask app
BASE_DIR = Path(__file__).resolve().parent

# Load prompts from JSON file
PROMPTS_FILE = BASE_DIR / "prompts.json"
if not PROMPTS_FILE.exists():
    raise FileNotFoundError(f"Prompts file not found at {PROMPTS_FILE}")

with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
    prompts = json.load(f)

timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
logger = lambda msg: print(f"{datetime.now()} - {msg}")  # Simple logger

# Directory to save generated cases and images
output_path = BASE_DIR / 'output/game'
output_path.mkdir(parents=True, exist_ok=True)

# Function to get a response from Gemini
def get_response_gemini(prompt: str) -> str:
    try:
        logger(f"Generating response for prompt: {prompt[:50]}...")
        model = genai.GenerativeModel('gemini-1.5-pro-001')
        response = model.generate_content(prompt)

        if response and response._result.candidates:
            content = response._result.candidates[0].content.parts[0].text.strip()
            logger(f"Received response: {content[:50]}...")
            return content
        else:
            logger("Empty or invalid response from Gemini.")
            return ""
    except Exception as err:
        logger(f"Error generating response: {err}")
        return ""

# Function to clean the response from code block formatting
def clean_response(response: str) -> str:
    if response.startswith("```python") and response.endswith("```"):
        return response[len("```python"): -len("```")].strip()
    return response

# Function to extract the list from the cleaned response
def extract_list(code: str) -> str:
    try:
        code = code.replace("\'", "\\'")  # Replacing every \' with \\'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.Expr)):  # Handle both named and unnamed lists
                if isinstance(node.value, ast.List):
                    extracted_list = ast.literal_eval(node.value)  # safely convert the list
                    return json.dumps(extracted_list)  # Convert to JSON
        return None
    except (SyntaxError, ValueError, TypeError) as e:
        logger(f"Error parsing or evaluating Python code: {e}")
        logger(f"Problematic code snippet: {code}")
        return None

def gen_cases(language: str, sex: str, age: int, output_dir: Path):
    logger("Starting to generate cases...")
    all_cases = []
    for i, option in enumerate(prompts['roles'], start=1):
        prompt = f"""{prompts['cases']} Respond in {language}. The content should be appropriate for a {sex} child aged {age}."""
        try:
            response = get_response_gemini(prompt)
            if not response:
                continue
            logger(f"Raw response for option {i}: {response}")
            cleaned_response = clean_response(response)
            logger(f"Cleaned response for option {i}: {cleaned_response[:50]}...")
            list_content = extract_list(cleaned_response)
            logger(f"Extracted list for option {i}: {list_content[:50]}...")
            parsed = json.loads(list_content)
            logger(f"Successfully parsed response for option {i}...")

            option_data = {'option_id': str(uuid.uuid4()), 'option': option, 'cases': []} # Generate option ID

            for j, case_data_dict in enumerate(parsed):
                case_id = str(uuid.uuid4()) # Generate case ID
                case_data = {'case_id': case_id, 'case': case_data_dict['case'], 'optimal': case_data_dict['optimal'], 'options': []}

                for k, option_data_dict in enumerate(case_data_dict['options']):
                    option_id = str(uuid.uuid4()) #Generate option ID
                    option_item = {'option_id': option_id, 'number': option_data_dict['number'], 'option': option_data_dict['option'],
                                    'health': option_data_dict['health'], 'wealth': option_data_dict['wealth'], 'relationships': option_data_dict['relationships'],
                                    'happiness': option_data_dict['happiness'], 'knowledge': option_data_dict['knowledge'], 'karma': option_data_dict['karma'],
                                    'time_management': option_data_dict['time_management'], 'environmental_impact': option_data_dict['environmental_impact'],
                                    'personal_growth': option_data_dict['personal_growth'], 'social_responsibility': option_data_dict['social_responsibility']}
                    case_data['options'].append(option_item)

                option_data['cases'].append(case_data)

            all_cases.append(option_data)
            case_file = output_dir / f"option_{i}.json"
            with open(case_file, 'w', encoding='utf-8') as f:
                json.dump(option_data, f, indent=4)
            logger(f"Saved case {i} to {case_file}")

        except Exception as e:
            logger(f"Error processing case {i}: {e}")
            return None
    return all_cases


# Generate images for cases
def gen_image_cases():
    image_output_path = BASE_DIR / 'output/images'
    image_output_path.mkdir(parents=True, exist_ok=True)
    logger("Generating images for cases...")

    for i, option in enumerate(prompts['roles'], start=1):
        prompt = prompts['image'].format(case=option)
        try:
            logger(f"Generating image for option {i}...")
            response = get_response_gemini(prompt)

            img_data = requests.get(response).content
            image = Image.open(BytesIO(img_data))
            image_path = image_output_path / f"option_{i}.png"
            image.save(image_path)
            logger(f"Image for option {i} saved at {image_path}")
        except Exception as err:
            logger(f"Error generating image for option {i}: {err}")
