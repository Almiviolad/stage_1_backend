from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///string_analyser.db'
app.config['JSON_SORT_KEYS'] = False

db = SQLAlchemy(app)

class String(db.Model):
    """String database model"""
    id = db.Column(db.String, primary_key=True)
    value = db.Column(db.String(200))
    length = db.Column(db.Integer)
    is_palindrome = db.Column(db.Boolean)
    unique_characters = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    sha256_hash = db.Column(db.String(50))
    char_map = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"{self.value} analysis"

with app.app_context():
    db.create_all()

def format_response(analysis):
    return {     
        "id": analysis.id,
        "value": analysis.value,
        "properties": {
        "length": analysis.length,
        "is_palindrome": analysis.is_palindrome,
        "unique_characters": analysis.unique_characters,
        "word_count": analysis.word_count,
        "sha256_hash": analysis.sha256_hash,
        "character_frequency_map": analysis.char_map,
        },
        "created_at": analysis.created_at.isoformat()
    }

@app.route("/strings", methods=['POST'])
def analyze():
    from analyser import String_analyser
    data = request.get_json(silent=True)
    if not data or 'value' not in data or not data['value']:
        return jsonify({"Error": 'Invalid request bdoy or missing "value" field'}), 400
    passed_value = data["value"]
    if not isinstance(passed_value, str):
        return jsonify({"Error": 'Invalid data type for value (must be string)'}), 422
    saved = String.query.filter_by(value=passed_value).first()
    if saved:
        return({"Error": "string already exists in the system"}), 409
    analysis = String_analyser(passed_value).save()
    return jsonify(format_response(analysis)), 201

def apply_filters(filters):
    query = String.query
    # Apply filters
    if "is_palindrome" in filters:
    	query = query.filter_by(is_palindrome=filters['is_palindrome'])
    
    if "min_length" in filters:
        query = query.filter(String.length >= filters['min_length'])
    if "max_length" in filters:
        query = query.filter(String.length <= filters['min_length'])
    if "word_count" in filters:
    	query = query.filter_by(word_count=filters['word_count'])
    
    if "contains_character" in filters:
        query = query.filter(String.value.contains(filters["contains_character"]))
        return query

@app.route("/strings", methods=["GET"])
def filter_strings():
    allowed_filters = {
        "is_palindrome": bool,
        "min_length": int,
        "max_length": int,
        "word_count": int,
        "contains_character": str
    }
    
    filters = {}
    
    # Validate query parameters
    for key, value in request.args.items():
        if key not in allowed_filters:
            return jsonify({"error": f"Invalid query parameter: {key}"}), 400
        
        expected_type = allowed_filters[key]
        try:
            if expected_type == bool:
                # Convert strings to true or false
                if value.lower() in ['true', '1']:
                    filters[key] = True
                elif value.lower() in ['false', '0']:
                    filters[key] = False
                else:
                    raise ValueError()
            else:
                filters[key] = expected_type(value)
        except ValueError:
            return jsonify({"error": f"Invalid value/type for {key}"}), 400
    
    # Start the query
    query = apply_filters(filters)       
    # Execute the query
    data = [format_response(s) for s in query.all()]
    count = len(data)
    result = {
    "data": data,
    "count":count,
    "filters_applied":filters
    }
    return jsonify(result), 200

@app.route("/strings/filter-by-natural-language", methods=["GET"])
def filter_by_nl():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400
    filters = {}
    query_lower = query.lower()

    # Word count
    if "single word" in query_lower or "one word" in query_lower:
        filters["word_count"] = 1
    elif "two words" in query_lower:
        filters["word_count"] = 2
        
        # Palindrome
    if "palindromic" in query_lower or "palindrome" in query_lower:
        filters["is_palindrome"] = True

    # Contains character
    vowels={"first":"a", "second":"e", "third":"i", "fourth":"o", "fifth":"u"}
    if "contains the" in query_lower:
        match = re.search(r"contains the  (\w+) vowel", query_lower)
        if match:
            position = match.group(1)
            filters["contains_character"] = vowels[position]
    if "containing the letter" in query_lower:
        # Extract letter
        import re
        match = re.search(r"containing the letter (\w)", query_lower)
        if match:
            filters["contains_character"] = match.group(1)

        # Strings longer than N
    match = re.search(r"longer than (\d+)", query_lower)
    if match:
        filters["min_length"] = int(match.group(1)) + 1
    query = apply_filters(filters)
    data = [format_response(s) for s in query.all()]
    count = len(data)
    result = {
        "data": data
        "count": count,
        "interpreted_query": {
            "original": query_lower
            "parsed_filters": filters
        }
    }
    return jsonify(result), 200

@app.route("/strings/<string_value>", methods=["DELETE"])
def delete_string(string_value):
    if not string_value:
        return jsonify({"error": "missing strung_value"}), 400
    string = String.query.filter_by(value=string_value)
    if not string:
        return jsonify({"error": "String does not exist in the system"}), 404
    db.session.delete(string)
    
if __name__== "__main__":
    app.run(debug=False)
