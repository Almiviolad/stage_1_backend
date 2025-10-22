from app.string_model import String, db
from collections import Counter
import hashlib
from datetime import datetime, timezone

def format_response(analysis):
    """firmats response unto json format, inserting required analytic attributes"""
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


def apply_filters(filters):
    """helper function to form query based on filters param passed"""
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

class String_analyser:
	""""
	class to analyse string input and save and give report
	"""
	def __init__(self, string):
		self.string = string
		self.clean_string = self.string.replace(" ", "").lower()
		self.length = len(self.string)
		self.is_palindrome = True if self.clean_string == self.clean_string[::-1] else False
		self.unique_chars = len(Counter(self.clean_string))
		self.word_count = len(self.string.split(" "))
		self.sha256_hash = hashlib.sha256(self.string.encode()).hexdigest()
		self.char_map = dict(Counter(self.clean_string))
		
	def save(self):
                
                analysis = String(value=self.string)
                analysis.id = self.sha256_hash
                analysis.value = self.string
                analysis.length = self.length
                analysis.is_palindrome = self.is_palindrome
                analysis.unique_characters = self.unique_chars
                analysis.word_count =self.word_count
                analysis.sha256_hash = self.sha256_hash
                analysis.char_map = self.char_map
                db.session.add(analysis)
                db.session.commit()
                
                return analysis
