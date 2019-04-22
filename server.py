from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json
from dnd_db import CharacterDB
from session_store import SessionStore
from http import cookies
from passlib.hash import bcrypt

gSessionStore = SessionStore()


class MyRequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        self.sendCookies()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)
        #put CORS stuff here too
        return

    def loadCookie(self):
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()
        return

    def sendCookies(self):
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())
        return

    def loadSession(self):
        self.loadCookie()
        if "sessionId" in self.cookie:
            sessionId = self.cookie["sessionId"].value
            self.session = gSessionStore.getSessionData(sessionId)
            if self.session == None:
                sessionId = gSessionStore.createSession()
                self.session = gSessionStore.getSessionData(sessionId)
                self.cookie["sessionId"] = sessionId
        else:
            sessionId = gSessionStore.createSession()
            self.session = gSessionStore.getSessionData(sessionId)
            self.cookie["sessionId"] = sessionId
        return

    def handleCharactersList(self):
        if self.isLoggedIn():
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            db = CharacterDB()
            characters = db.getAllCharacters()
            self.wfile.write(bytes(json.dumps(characters), "utf-8"))
        else:
            self.handle401()

    def isLoggedIn(self):
        if "userId" in self.session:
            return True
        else:
            return False

    def handleUsersCreate(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("the text body:", body)
        parsed_body = parse_qs(body)
        print("the parsed body:", parsed_body)

        # save the new user!
        
        firstName = parsed_body["firstName"][0]
        lastName = parsed_body["lastName"][0]

        username = parsed_body["username"][0]
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]
        e = bcrypt.hash(password)

        db = CharacterDB()
        emailInDatabase = db.getUser(email)

        if emailInDatabase == None:
            db.createUser(firstName, lastName, username, email, e)
            self.send_response(201)
            self.end_headers()
        else:
            self.send_response(422)
            self.end_headers()

        

        # register a new user
        # eventually: validate the the user doesn't already exists (422 if used)
        # capture inputs: first/last name, email, password
        # encrypt password: e = bcyrpt.hash(password)
        # save ^^^ to the DB as a new user
        return

    def handleSessionCreate(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("the text body:", body)
        parsed_body = parse_qs(body)
        print("the parsed body:", parsed_body)
        
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]
        # authenticate an existing user
        # capture inputs: email, password
        # find user in DB by email address

        db = CharacterDB()
        user = db.getUser(email)

        # code below
        if user == None:
            self.handle401()
        else:
            if bcrypt.verify(password, user["password"]):
                self.session["userId"] = user["id"]
                self.send_response(201)
                self.end_headers()
            else:
                self.handle401()
        return

    def handleCharactersCreate(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("the text body:", body)
        parsed_body = parse_qs(body)
        print("the parsed body:", parsed_body)

        # save the character!
        #CHARACTERS.append(parsed_body["name"][0])
        
        name = parsed_body["name"][0]
        level = parsed_body["level"][0]

        cclass = parsed_body["cclass"][0]
        race = parsed_body["race"][0]
        alignment = parsed_body["alignment"][0]
        XP = parsed_body["XP"][0]

        db = CharacterDB()
        db.createCharacter(name, level, cclass, race, alignment, XP)

        self.send_response(201)
        self.end_headers()

    def handleCharactersUpdate(self, id):
        db = CharacterDB()
        character = db.getCharacter(id)
        

        if character == None:
            self.handleNotFound()
        else:
            length = self.headers["Content-length"]
            body = self.rfile.read(int(length)).decode("utf-8")
            print("the text body:", body)
            parsed_body = parse_qs(body)
            print("the parsed body:", parsed_body)

            # save the character!
            #CHARACTERS.append(parsed_body["name"][0])
            
            name = parsed_body["name"][0]
            level = parsed_body["level"][0]
            cclass = parsed_body["cclass"][0]
            race = parsed_body["race"][0]
            alignment = parsed_body["alignment"][0]
            XP = parsed_body["XP"][0]

            db.updateCharacter(name, level, cclass, race, alignment, XP, id)

            self.send_response(201)
            self.end_headers()

    def handleCharactersDelete(self, id):
        db = CharacterDB()
        character = db.getCharacter(id)
        

        if character == None:
            self.handleNotFound()
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            db.deleteCharacter(id)
            self.wfile.write(bytes(json.dumps(characters), "utf-8"))

    def handleCharactersRetrieve(self, id):
        db = CharacterDB()
        character = db.getCharacter(id)
        

        if character == None:
            self.handleNotFound()
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(character), "utf-8"))

    def handleNotFound(self):
        self.send_response(404)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("404 Not Found", "utf-8"))

    def handle401(self):
        self.send_response(401)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("401", "utf-8"))

    def do_OPTIONS(self):
        self.loadSession()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-type")
        self.end_headers()


    def do_GET(self):
        self.loadSession()
        parts = self.path.split('/')[1:]
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None

        if collection == "dndCharacters":
            if id == None:
                self.handleCharactersList()
            else:
                self.handleCharactersRetrieve(id)
        else:
            self.handleNotFound()

    def do_POST(self):
        self.loadSession()
        if self.path == "/dndCharacters":
            self.handleCharactersCreate()
        elif self.path == "/dndSessions":
            self.handleSessionCreate()
        elif self.path == "/dndUsers":
            self.handleUsersCreate()
        else:
            self.handleNotFound()

    def do_DELETE(self):
        self.loadSession()
        parts = self.path.split('/')[1:]
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None

        if collection == "dndCharacters":
            if id == None:
                self.handleNotFound()
            else:
                self.handleCharactersDelete(id)
        else:
            self.handleNotFound()

    def do_PUT(self):
        self.loadSession()
        parts = self.path.split('/')[1:]
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None

        if collection == "dndCharacters":
            if id == None:
                self.handleNotFound()
            else:
                self.handleCharactersUpdate(id)
        else:
            self.handleNotFound()

def run():
    db = CharacterDB()
    db.createCharactersTable()
    db.createUsersTable()
    db = None # disconnect

    listen = ("0.0.0.0", 8080)
    server = HTTPServer(listen, MyRequestHandler)

    print("Listening...")
    server.serve_forever()

run()
