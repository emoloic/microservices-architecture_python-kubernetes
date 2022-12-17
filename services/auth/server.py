import jwt, datetime, os, bcrypt
from flask import Flask, request
from flaskext.mysql import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_DATABASE_HOST"] = os.getenv("MYSQL_DATABASE_HOST")
server.config["MYSQL_DATABASE_USER"] = os.getenv("MYSQL_DATABASE_USER")
server.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_DATABASE_PASSWORD")
server.config["MYSQL_DATABASE_DB"] = os.getenv("MYSQL_DATABASE_DB")
server.config["MYSQL_DATABASE_PORT"] = int(os.getenv("MYSQL_DATABASE_PORT"))

mysql.init_app(server)

@server.route("/registration", methods=["POST"])
def register():
    data = request.get_json(force=True)
    email = data["email"]
    password = data["password"]
    
    # converting password to array of bytes
    bytes = password.encode('utf-8')
    # generating the salt
    salt = bcrypt.gensalt()
    # Hashing the password
    password_hash = bcrypt.hashpw(bytes, salt)
    
    # Check if the user already exists
    cur = mysql.get_db().cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (username,)
    )

    if res > 0:
        return "Email already exists", 401
    else:
        res = cur.execute(
            "INSERT INTO user (email, password) VALUES(%s, %s)", (username, password_hash.decode('utf-8'))
        )
        mysql.get_db().commit()
        return "User created", 201

@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    # Check db for username and password
    cur = mysql.get_db().cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )

    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]
        password_verification = bcrypt.checkpw(auth.password.encode('utf-8'), password.encode('utf-8'))

        if auth.username != email or (password_verification is False):
            return "Invalid credentials", 401
        else:
            return createJWT(auth.username, str(os.getenv("JWT_SECRET")), True) 
    else:
        return "Invalid credentials", 401

@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401
    
    if encoded_jwt.split(" ")[0] != "Bearer":
        return "Only accept Bearer token", 401
    
    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt, str(os.getenv("JWT_SECRET")), algorithms=["HS256"]
        )
    except:
        return "not authorized", 403
    
    return decoded, 200

def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username, # username
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1), # expiration after 1 day
            "iat": datetime.datetime.utcnow(), # When the token was issued
            "admin": authz, # Whether or not the user is an admin
        },
        secret,
        algorithm="HS256",
    )

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)  