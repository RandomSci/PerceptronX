import bcrypt
import mysql.connector
from connections.functions import *


def get_Mysql_db(): #Mysql
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="perceptronx"
    )


def Register_User_Web(first_name, last_name, company_email, password):
    db = get_Mysql_db()
    cursor = db.cursor()
    
    hashed_password = bcrypt.hashpw(password.password.encode("utf-8"), bcrypt.gensalt())
    
    try:
        cursor.execute("SELECT COUNT(*) FROM Therapists WHERE first_name = %s AND last_name = %s", (first_name, last_name))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="Username or email already exists.")

        cursor.execute(
            "INSERT INTO Therapists (first_name, last_name, company_email, password) VALUES (%s, %s, %s)",
            (first_name, last_name, company_email, hashed_password.decode("utf-8"))
        )
        db.commit()
    except mysql.connector.IntegrityError:
            return {"error": "Username or email already exists."}
    finally:
        cursor.close()
        db.close()