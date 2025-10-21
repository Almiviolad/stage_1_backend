from collections import Counter
import hashlib
from datetime import datetime, timezone

class String_analyser:
	""""
	class to analyse string input and give report
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
                from app import String, db
                
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
