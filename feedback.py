import logging
import uuid
from database import Database

class Feedback:
	def __init__(self, client=None):
		self.client = client
		if not type(self.client) is dict:
			self.client = {}
		self.db = Database()
	
	def result(self, is_know, label, reason, quuid):
		result = {}
		try:
			if self.db.is_query_exist(quuid):
				self.db.insert_result_feedback(quuid, is_know, reason, label, self.client["ip"], self.client["browser"])
				result["status"] = "Success"
				result["message"] = "Result feedback noted"
			else:
				result["status"] = "Failed"
				result["message"] = "Invalid quuid"				
		except Exception, e:
			result["status"] = "Failed"
			result["message"] = "Database error"
			result["detail"] = str(e)
		return result

	def reference(self, is_related, label, reason, auuid):
		result = {}
		try:
			if self.db.is_reference_exist(auuid):
				self.db.insert_reference_feedback(auuid, is_related, reason, label, self.client["ip"], self.client["browser"])
				result["status"] = "Success"
				result["message"] = "Reference feedback noted"
			else:
				result["status"] = "Failed"
				result["message"] = "Invalid auuid"		
		except Exception, e:
			result["status"] = "Failed"
			result["message"] = "Database error"
			result["detail"] = str(e)
		return result