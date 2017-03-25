import mysql.connector
from datetime import date, datetime
import json
import config

class Database:
	def __init__(self):
		self.conn = mysql.connector.connect(user=config.mysql_credentials["user"], \
																				password=config.mysql_credentials["password"], \
																				host=config.mysql_credentials["host"], \
																				database=config.mysql_credentials["database"])
		self.cur = self.conn.cursor(buffered=True)

	def __enter__(self):
		return DBase()

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.conn:
			self.cur.close()
			self.conn.close()

	def insert_query_log(self, lhash, text, search, qhash, ip, browser): 	
		sql = "INSERT INTO log_query (log_hash, query_text, query_search, query_hash, query_time, client_ip, client_browser) VALUES" + \
					"({}, {}, {}, '{}', '{}', '{}', {})".format(json.dumps(lhash), json.dumps(text), json.dumps(search), qhash, datetime.now(), ip, json.dumps(browser))
		self.cur.execute(sql)
		self.conn.commit()
		return self.cur.lastrowid

	def insert_result_log(self, qid, hoax, fact, unknown, unrelated, conclusion):
		sql = "INSERT INTO log_result (id_query, finished_at, hoax_score, fact_score, unknown_score, unrelated_score, conclusion) VALUES" + \
					"('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (qid, datetime.now(), hoax, fact, unknown, unrelated, conclusion)
		self.cur.execute(sql)
		self.conn.commit()
		return self.cur.lastrowid

	def insert_result_feedback(self, qhash, is_know, reason, label, ip, browser):
		sql = "INSERT INTO feedback_result (query_hash, reported_at, is_know, reason, feedback_label, client_ip, client_browser) VALUES" + \
					"('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (qhash, datetime.now(), is_know, reason, label, ip, browser)
		self.cur.execute(sql)
		self.conn.commit()
		return self.cur.lastrowid

	def insert_reference_feedback(self, ahash, is_relevant, reason, label, ip, browser):
		print(str(ahash))
		print(str(is_relevant))
		sql = "INSERT INTO feedback_reference (article_hash, reported_at, is_relevant, reason, feedback_label, client_ip, client_browser) VALUES" + \
					"('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (ahash, datetime.now(), is_relevant, reason, label, ip, browser)
		self.cur.execute(sql)
		self.conn.commit()
		return self.cur.lastrowid

	def insert_references(self, qid, articles):
		insert_values = []
		for article in articles:
			insert_values.append((qid, str(article["qhash"]), str(article['hash']), str(article['date']), str(article['url']), article['content'], datetime.now())) 	
		sql = "INSERT INTO article_reference (id_query, query_hash, article_hash, article_date, article_url, article_content, retrieved_at) VALUES" + \
				",".join("(%s, %s, %s, %s, %s, %s, %s)" for _ in insert_values)
		flattened_values = [item for sublist in insert_values for item in sublist]		
		self.cur.execute(sql, flattened_values)
		self.conn.commit()

	def is_query_exist(self, loghash):
		sql = "SELECT id FROM log_query WHERE log_hash = '%s'" % (loghash)
		self.cur.execute(sql)
		self.conn.commit()
		return (self.cur.rowcount == 1)

	def is_reference_exist(self, ahash):
		sql = "SELECT id FROM article_reference WHERE article_hash = '%s'" % (ahash)
		self.cur.execute(sql)
		self.conn.commit()
		return (self.cur.rowcount == 1)

	def get_query_by_loghash(self, loghash):
		sql = "SELECT * FROM log_query WHERE log_hash = '%s'" % (loghash)
		self.cur.execute(sql)
		self.conn.commit()
		query = self.cur.fetchone()
		return query

	def get_query_log(self):
		sql = "SELECT * FROM log_query ORDER BY query_time DESC"
		self.cur.execute(sql)
		self.conn.commit()
		queries = []
		for row in self.cur.fetchall():
			query = {}
			query["log_hash"] = row[1]
			query["query_text"] = row[2]
			query["query_search"] = row[3]
			query["query_hash"] = row[4]
			query["query_time"] = str(row[5])
			query["client_ip"] = row[6]
			query["client_browser"] = row[7]
			query["clicked"] = row[8]
			queries.append(query)
		return queries

	def get_reference_by_qhash(self, qhash):
		sql = "SELECT * FROM article_reference WHERE query_hash = '%s'" % (qhash)
		self.cur.execute(sql)
		self.conn.commit()
		articles = []
		if (self.cur.rowcount > 0):
			for row in self.cur.fetchall():
				article = {}
				article["hash"] = row[3]
				article["date"] = row[4]
				article["url"] = row[5]
				article["content"] = row[6]
				articles.append(article)
		return articles

	def get_reference_feedback(self):
		## VIWEW HELPER #1
		sql = "CREATE OR REPLACE VIEW feedback_reference_result AS SELECT article_hash, is_relevant, feedback_label, COUNT(*) AS count FROM feedback_reference GROUP BY article_hash, is_relevant, feedback_label"
		self.cur.execute(sql)
		self.conn.commit()

		## VIWEW HELPER #2
		sql = "CREATE OR REPLACE VIEW feedback_reference_max AS (SELECT article_hash, is_relevant, feedback_label, count FROM feedback_reference_result WHERE count = (SELECT MAX(count) FROM feedback_reference_result i WHERE i.article_hash = feedback_reference_result.article_hash))"
		self.cur.execute(sql)
		self.conn.commit()

		## THE QUERY
		sql = "SELECT log_query.id, log_query.query_text, log_query.query_search, article_reference.article_content, feedback_reference_max.is_relevant, feedback_reference_max.feedback_label FROM feedback_reference_max LEFT JOIN article_reference ON article_reference.article_hash = feedback_reference_max.article_hash LEFT JOIN log_query ON log_query.id = article_reference.id_query"
		self.cur.execute(sql)
		self.conn.commit()

		feedbacks = {}
		for row in self.cur.fetchall():
			feedback = {}
			feedback["query_text"] = row[1]
			feedback["query_search"] = row[2]
			feedback["article_content"] = row[3]
			feedback["is_relevant"] = row[4]
			feedback["feedback_label"] = row[5]
			#feedbacks.append(feedback)
			if not (row[0] in feedbacks):
				feedbacks[row[0]] = []
			feedbacks[row[0]].append(feedback)
		return feedbacks

	def check_query(self, qhash): 	
		sql = "INSERT INTO log_query (query_text, query_search, query_hash, query_time, client_ip, client_browser) VALUES" + \
					"({}, {}, '{}', '{}', '{}', {})".format(json.dumps(text), json.dumps(search), qhash, datetime.now(), ip, json.dumps(browser))
		self.cur.execute(sql)
		self.conn.commit()
