from flask import Flask, request, jsonify
import re
from app.utils import String_analyser, apply_filters, format_response
from app.string_model import String, db


def register_routes(app):
    @app.route("/strings", methods=["POST"])
    def analyze():
        data = request.get_json(silent=True)
        if not data or "value" not in data or not data["value"]:
            return (
                jsonify({"error": 'Invalid request body or missing "value" field'}),
                400,
            )

        passed_value = data["value"]
        if not isinstance(passed_value, str):
            return (
                jsonify({"error": "Invalid data type for value (must be string)"}),
                422,
            )

        saved = String.query.filter_by(value=passed_value).first()
        if saved:
            return jsonify({"error": "String already exists in the system"}), 409

        analysis = String_analyser(passed_value).save()
        return jsonify(format_response(analysis)), 201

    @app.route("/strings/<string_value>", methods=["GET"])
    def get_string_analysis(string_value):
        analysis = String.query.filter_by(value=string_value).first()
        if not analysis:
            return (
                jsonify(
                    {"error": "404 Not Found: String does not exist in the system"}
                ),
                404,
            )
        return jsonify(format_response(analysis)), 200

    @app.route("/strings", methods=["GET"])
    def filter_strings():
        allowed_filters = {
            "is_palindrome": bool,
            "min_length": int,
            "max_length": int,
            "word_count": int,
            "contains_character": str,
        }

        filters = {}
        for key, value in request.args.items():
            if key not in allowed_filters:
                return jsonify({"error": f"Invalid query parameter: {key}"}), 400

            expected_type = allowed_filters[key]
            try:
                if expected_type == bool:
                    if value.lower() in ["true", "1"]:
                        filters[key] = True
                    elif value.lower() in ["false", "0"]:
                        filters[key] = False
                    else:
                        raise ValueError()
                else:
                    filters[key] = expected_type(value)
            except ValueError:
                return jsonify({"error": f"Invalid value/type for {key}"}), 400

        query_result = apply_filters(filters)
        result = query_result.all()
        if not result:
            return jsonify({"error":"No match foind"}), 404
        data = [format_response(s) for s in result]
        count = len(data)
        return jsonify({"data": data, "count": count, "filters_applied": filters}), 200

    @app.route("/strings/filter-by-natural-language", methods=["GET"])
    def filter_by_nl():
        query_text = request.args.get("query")
        if not query_text:
            return jsonify({"error": "No query provided"}), 400

        filters = {}
        query_lower = query_text.lower()

        if "single word" in query_lower or "one word" in query_lower:
            filters["word_count"] = 1
        elif "two words" in query_lower:
            filters["word_count"] = 2

        if "palindromic" in query_lower or "palindrome" in query_lower:
            filters["is_palindrome"] = True

        vowels = {
            "first": "a",
            "second": "e",
            "third": "i",
            "fourth": "o",
            "fifth": "u",
        }
        match = re.search(r"contain the (\w+) vowel", query_lower) or re.search(r'containing the (\w+) vowel', query_lower)
        if match:
            position = match.group(1)
            if position in vowels:
                filters["contains_character"] = vowels.get(position)

        match = re.search(r"containing the letter (\w)", query_lower) or re.search(r'contain the letter(\w)', query_lower)
        if match:
            filters["contains_character"] = match.group(1)

        match = re.search(r"longer than (\d+)", query_lower)
        if match:
            filters["min_length"] = int(match.group(1)) + 1

        match = re.search(r"shorter than (\d+)", query_lower)
        if match:
            filters["max_length"] = int(match.group(1)) - 1

        if not filters:
            return jsonify({"error": "Unable to parse natural language query"}), 400

        if (
            "min_length" in filters
            and "max_length" in filters
            and filters["min_length"] > filters["max_length"]
        ):
            return (
                jsonify({"error": "Query parsed but resulted in conflicting filters"}),
                422,
            )

        query_result = apply_filters(filters).all()
        if not query_result:
            return jsonify({"error":"No match found"}), 404
        data = [format_response(s) for s in query_result]
        count = len(data)

        return (
            jsonify(
                {
                    "data": data,
                    "count": count,
                    "interpreted_query": {
                        "original": query_lower,
                        "parsed_filters": filters,
                    },
                }
            ),
            200,
        )

    @app.route("/strings/<string_value>", methods=["DELETE"])
    def delete_string(string_value):
        string = String.query.filter_by(value=string_value).first()
        if not string:
            return jsonify({"error": "String does not exist in the system"}), 404

        db.session.delete(string)
        db.session.commit()
        return '', 204
