import sqlite3


class Database:

	def __init__(self, db_file):
		self.connection = sqlite3.connect(db_file)
		self.cursor = self.connection.cursor()

		try:
			self.connection.execute(f"SELECT * FROM webhooks")
		except sqlite3.OperationalError as error:
			self.connection.execute('''CREATE TABLE IF NOT EXISTS webhooks (
webhookid   INTEGER,
channelid   INTEGER,
channelfrom INTEGER,
webhook     TEXT,
language    TEXT
);''')

	def create_webhook(self, webhookid, channelid, channelfrom, webhook, language):
		with self.connection:
			return self.connection.execute(f"INSERT INTO webhooks VALUES ('{webhookid}', '{channelid}', '{channelfrom}', '{webhook}', '{language}')")

	def delete_webhook(self, webhookid):
		with self.connection:
			return self.connection.execute("DELETE FROM webhooks WHERE webhookid = ?", (webhookid,))

	def get_webhookurl(self, channelfrom):
		with self.connection:
			return self.connection.execute("SELECT webhook, language FROM webhooks WHERE channelfrom = ?", (channelfrom,)).fetchall()

	def get_webhooks(self, channelid):
		with self.connection:
			cid = self.connection.execute("SELECT webhookid FROM webhooks WHERE channelid = ?", (channelid,)).fetchall()

			return [e[0] for e in cid]
