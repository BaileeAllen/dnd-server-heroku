import os
import psycopg2
import psycopg2.extras
import urllib.parse

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

class CharacterDB:

	def __init__(self):
		urllib.parse.uses_netloc.append("postgres")
		url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

		self.connection = psycopg2.connect(cursor_factory=psycopg2.extras.RealDictCursor, database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
		self.cursor = self.connection.cursor()


	def __del__(self):
		#disconnect!
		self.connection.close()

	def createCharactersTable(self):
		self.cursor.execute("CREATE TABLE IF NOT EXISTS characters (id serial PRIMARY KEY, name VARCHAR(255), level VARCHAR(255), race VARCHAR(255), cclass VARCHAR(255), alignment VARCHAR(255), XP serial)")
		self.connection.commit()
		return

	def createUsersTable(self):
		self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id serial PRIMARY KEY, firstname VARCHAR(255), lastname VARCHAR(255), username VARCHAR(255), email VARCHAR(255), password VARCHAR(255))")
		self.connection.commit()
		return


	def createCharacter(self, name, level, race, cclass, alignment, XP):
		sql = "INSERT INTO characters (name, class, race, level, alignment, XP) VALUES(%s, %s, %s, %s, %s, %s)"
		self.cursor.execute(sql, [name, cclass, race, level, alignment, XP])
		self.connection.commit()
		return

	def deleteCharacter(self, id):
		sql = "DELETE FROM characters WHERE id = %s"
		self.cursor.execute(sql, [id])
		self.connection.commit()
		return

	def updateCharacter(self, name, level, race, cclass, alignment, XP, id):
		sql = "UPDATE characters SET name=%s, level=%s, race=%s, class=%s, alignment=%s, XP=%s WHERE id=%s"
		self.cursor.execute(sql, [name, cclass, race, level, alignment, XP, id])
		self.connection.commit()
		return

	def getAllCharacters(self):
		self.cursor.execute("SELECT * FROM characters")
		return self.cursor.fetchall()

	def getCharacter(self, id):
		sql = "SELECT * FROM characters WHERE id = %s"
		self.cursor.execute(sql, [id]) #data must be a list
		return self.cursor.fetchone()

	def getUser(self, email):
		sql = "SELECT * FROM users WHERE email = %s"
		self.cursor.execute(sql, [email]) #data must be a list
		return self.cursor.fetchone()

	def createUser(self, firstName, lastName, username, email, password):
		sql = "INSERT INTO users (firstname, lastname, username, email, password) VALUES(%s, %s, %s, %s, %s)"
		self.cursor.execute(sql, [firstName, lastName, username, email, password])
		self.connection.commit()
		return