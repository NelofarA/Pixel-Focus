from flask import Flask, render_template, request, redirect, url_for, make_response, session, flash, jsonify
import hashlib
import sqlite3
import os 
import random

app = Flask(__name__)

app.secret_key = "secrettunnelthruthemountains"

#Login route
@app.route("/login", methods=["GET", "POST"])
def login(): 
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "Username and password cannot be empty!"
            
        if verify_login(username, password):
            session["username"] = username
            return redirect(url_for("home"))
        
        else:
            return "Invalid username or password!"
    
    return render_template("login.html")

# ADDING HASHING + started sign up you can change the variables if you need to 
# when creating the actually sign up html. IF you have any questions about
# this message me!  -Sarah 
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """TODO: register's user, NOT WORKING AS FORM FOR signup is NOT made yet!!!"""
    # Done - Gavi
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "Username or password cannot be empty!"
        
        if create_user(username, password):
            return redirect(url_for("login"))
        else:
            return "Error, this username is already taken or error has occured"
    return render_template("signup.html")
    #TODO: make signup.html form
    
# added password protection section + connection to database - Sarah
def create_user(username, password):
    """Function adds salt and hashes passwords then save/updates on database"""
    salt = os.urandom(7)
    salt_password = salt + password.encode()
    hash_ = hashlib.new("SHA256")
    hash_.update(salt_password) 
    hash_password = hash_.hexdigest()

    try: 
        with sqlite3.connect("database.db") as conn:
            #You can actually open it same way as a file (like with open(file))
            #like a file it closes connection at the end in with block
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO users (username, password, salt)
                            VALUES (?, ?, ?);""",
                            (username, hash_password, salt.hex())
                            )
            # note: salt has to be in hex to be printed out
         
            conn.commit()
            return True
    except sqlite3.Error: 
       # conn.rollback()
        print("Sorry an error has occured")
        return False
    #finally:
       # conn.close()
    #dont need conn.close() or conn.rollback() cause it is in a with block
    #closes automatically 
    
# added password protection section - Sarah
def verify_login(username, password_input) -> bool:
    """
    Called from form submition, function connects to database and hashes
    inputed password with salt and check if it matches saved hashed password
    returns a bool value so when it goes out of function back to form sumbition
    it will proceed if true
    """
    try:
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            query = """SELECT password, salt FROM users WHERE username = ? ;"""
                
            cursor.execute(query, (username,)) 
            row = cursor.fetchone()
            
            if row: 
                stored_password, salt_hex = row
                hash_ = hashlib.new("SHA256")
                stored_salt = bytes.fromhex(salt_hex)
                salt_password = stored_salt + password_input.encode()
                hash_.update(salt_password)
                salt_password = hash_.hexdigest()

                if salt_password == stored_password:
                    print("Login successful")
                    return True

            else:
                print("Login Failed")
                return False
            
    except sqlite3.Error: 
        print("Sorry an error has occured")
        return False

# Change password route
@app.route("/changePassword", methods=["GET","POST"])
def changePassword():
    # if "username" not in session:
        # return redirect(url_for("login"))
    
    if request.method == "POST":
        #username = session["username"]
        username = request.form.get("username")
        new_password = request.form.get("newPassword")
    
        salt = os.urandom(7)
        salt_password = salt + new_password.encode()
        hash_ = hashlib.new("SHA256")
        hash_.update(salt_password) 
        new_hash_password = hash_.hexdigest()

        try: 
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users 
                    SET password=?, salt=?
                    WHERE username=?;
                    """, (new_hash_password, salt.hex(), username))
                # note: salt has to be in hex to be printed out
             
                conn.commit()
                flash("Password update successful!")
                #print("Password update successful!")
                return redirect(url_for("login"))
                
        except sqlite3.Error: 
            print("Sorry, there was an error updating your password")
            return render_template("changePassword.html")
    
    return render_template("changePassword.html")

# Route for homepage (redirects to log in page if the user is not signed in)
@app.route("/")
def home():
    if "username" not in session:
        return render_template("login.html")
        
    username = session["username"]
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT uid FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        print("User not found")
        return render_template("login.html")

    user_id = user[0]
    conn.close()
    
    userInfo = get_user_info(user_id)
    
    skillInfo = []
    skills = get_user_skills(user_id)
    
    for skill in skills:
        name = skill[1]
        time = get_time_spent(user_id, name)
        avg = get_quiz_avg(user_id, name)
        skillInfo.append({
            "skill_id": skill[0],
            "name": name,
            "time_spent": time,
            "accuracy": avg
        })
    
    return render_template("home.html", username=session["username"], skills=skillInfo, userInfo=userInfo)

#Get user info (id, name, level, xp) and save as a dictionary
def get_user_info(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, level, xp
        FROM users
        WHERE uid=? """, (user_id,))
    info = cursor.fetchone()
    conn.close()
    
    result = {
        "user_id": user_id,
        "username": info[0],
        "level": info[1],
        "xp": info[2]}
    #LEVEL HAS A DUMMY VALUE REPLACE IT WITH info[1] LATER
    
    return result

#Get time spent on every skill
def get_time_spent(user_id, name):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT time_spent
        FROM skills
        WHERE name=? AND user_id=? """, (name,user_id))
    time = cursor.fetchone()
    conn.close()
    return time[0]
    
#Get avg score for each skill
def get_quiz_avg(user_id, name):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT quiz_avg
        FROM skills
        WHERE name=? AND user_id=? """, (name,user_id))
    avg = cursor.fetchone()
    conn.close()
    return avg[0]   

# Route for logout (redirects to login page)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# About Us Route   
@app.route("/aboutUs")
def aboutUs():
    return render_template("aboutUs.html")

@app.route("/flashcards")
def flashcards():
    if "username" not in session:
       return redirect(url_for("login"))
    username = session["username"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT uid FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "User not found"

    user_id = user[0]

    cursor.execute("SELECT skill_id, name FROM skills WHERE user_id=?", (user_id,))
    skills = cursor.fetchall()
    conn.close()

    return render_template("flashcards.html", skills=skills)

@app.route("/add_skill", methods=["POST"])
def add_skill():
    if "username" not in session:
        return redirect(url_for("login"))

    skill_name = request.form.get("skill_name")
    if not skill_name:
        return redirect(url_for("flashcards"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT uid FROM users WHERE username=?", (session["username"],))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return redirect(url_for("flashcards"))

    user_id = row[0]

    cursor.execute("SELECT COUNT(*) FROM skills WHERE user_id=?", (user_id,))
    if cursor.fetchone()[0] >= 5:
       
        conn.close()
        return render_template("flashcards.html", skills=get_user_skills(user_id), error="You can only have 5 skills!")

    cursor.execute(
        "INSERT INTO skills (user_id, name) VALUES (?, ?)",
        (user_id, skill_name)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("flashcards")) 

def get_user_skills(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT skill_id, name FROM skills WHERE user_id=?", (user_id,))
    skills = cursor.fetchall()
    conn.close()
    return skills

@app.route("/delete_skill/<int:skill_id>", methods=["POST"])
def delete_skill(skill_id):
    if "username" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

   
    cursor.execute("""
        SELECT s.skill_id FROM skills s
        JOIN users u ON s.user_id = u.uid
        WHERE s.skill_id=? AND u.username=?
    """, (skill_id, session["username"]))
    if not cursor.fetchone():
        conn.close()
        return redirect(url_for("flashcards"))

    cursor.execute("DELETE FROM flashcards WHERE skill_id=?", (skill_id,))
    cursor.execute("DELETE FROM skills WHERE skill_id=?", (skill_id,))

    conn.commit()
    conn.close()
    return redirect(url_for("flashcards"))


@app.route("/skill/<int:skill_id>", methods=["GET", "POST"])
def view_skill(skill_id):
    if "username" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.name FROM skills s
        JOIN users u ON s.user_id = u.uid
        WHERE s.skill_id = ? AND u.username = ?
    """, (skill_id, session["username"]))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return "Skill not found or you don't have access."

    skill_name = row[0]

    if request.method == "POST":
        front = request.form.get("front").strip()
        back = request.form.get("back").strip()
        if front and back:
            cursor.execute("INSERT INTO flashcards (skill_id, front, back) VALUES (?, ?, ?)",
                           (skill_id, front, back))
            cursor.execute(
            "UPDATE skills SET flashcard_count = flashcard_count + 1 WHERE skill_id=?",
            (skill_id,)
            )
            conn.commit()


    cursor.execute("SELECT flashcard_id, front, back FROM flashcards WHERE skill_id=?", (skill_id,))
    flashcards = cursor.fetchall()
    conn.close()

    return render_template("view_skill.html", skill_name=skill_name, skill_id=skill_id, flashcards=flashcards)


@app.route("/delete_flashcard/<int:flashcard_id>", methods=["POST"])
def delete_flashcard(flashcard_id):
    if "username" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT f.skill_id
        FROM flashcards f
        JOIN skills s ON f.skill_id = s.skill_id
        JOIN users u ON s.user_id = u.uid
        WHERE f.flashcard_id = ? AND u.username = ?
    """, (flashcard_id, session["username"]))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return "Flashcard not found or you don't have permission."
    
    skill_id=row[0]

    
    cursor.execute("DELETE FROM flashcards WHERE flashcard_id=?", (flashcard_id,))
    cursor.execute( "UPDATE skills SET flashcard_count = flashcard_count - 1 WHERE skill_id=?",
    (skill_id,))
    

    conn.commit()
    conn.close()

    return redirect(request.referrer or url_for("flashcards"))


@app.route("/quizzes", methods=["GET", "POST"])
def quizzes():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    
    cursor.execute("SELECT uid FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return "User not found"
    user_id = user[0]

    
    cursor.execute("""
        SELECT skill_id, name 
        FROM skills 
        WHERE user_id=? AND flashcard_count >= 10
    """, (user_id,))
    skills = cursor.fetchall()
    conn.close()

    if request.method == "POST":
        selected_skill_id = request.form.get("skill_id")
        if selected_skill_id:
            return redirect(url_for("take_quiz", skill_id=selected_skill_id))

    return render_template("quizzes.html", skills=skills)
    
@app.route("/take_quiz/<int:skill_id>", methods=["GET", "POST"])
def take_quiz(skill_id):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT uid FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return "User not found"
    user_id = user[0]

    #get all flashcards
    cursor.execute("SELECT flashcard_id, front, back FROM flashcards WHERE skill_id=?", (skill_id,))
    all_flashcards = cursor.fetchall()
    
    if not all_flashcards:
        conn.close()
        return "No flashcards found for this skill."

    if request.method == "POST":
        saved_flashcards = session.get(f'quiz_flashcards_{skill_id}')
        if not saved_flashcards:
            conn.close()
            return "Quiz session expired. Please start over."
        
        # calculate score using the saved flashcards
        score = 0
        total = len(saved_flashcards)
        results = []

        for flashcard_id, front, back in saved_flashcards:
            user_answer = request.form.get(f"flashcard_{flashcard_id}", "").strip()
            correct = user_answer.lower() == back.lower()
            results.append((front, back, user_answer, correct))
            if correct:
                score += 1
        
        percent_score = int((score / total) * 100)

        cursor.execute("""
            UPDATE skills SET quiz_avg = (quiz_avg * total_quizzes_taken + ?) / (total_quizzes_taken + 1),
                total_quizzes_taken = total_quizzes_taken + 1
            WHERE skill_id = ?
        """, (percent_score, skill_id))

     
        award = 0
        if percent_score == 100:
            award = 20
        elif percent_score >=90:
            award = 15
        elif percent_score >= 70:
            award = 10

        
    

        cursor.execute("UPDATE users SET xp = xp + ? WHERE uid=?", ( award,user_id))
        update_level(cursor, user_id)

      
        session.pop(f'quiz_flashcards_{skill_id}', None)
        
        conn.commit()
        conn.close()

        return render_template("quiz_result.html", results=results, percent_score=percent_score)

    
    if len(all_flashcards) >= 10:
        quiz_flashcards = random.sample(all_flashcards, 10)
    else:
        quiz_flashcards = all_flashcards
    
    # this makes sure we save our randomly selected questions into the sessin so that we can display the result later
    #f[0] is the skill_id
    #f[1] is the flashcard front and 
    #f[2] is the back of the flashcard
    quiz_data = []
    for flashcard in quiz_flashcards:
        quiz_data.append((flashcard[0], flashcard[1], flashcard[2]))
        session[f'quiz_flashcards_{skill_id}'] = quiz_data


    
    conn.close()
    return render_template("take_quiz.html", flashcards=quiz_flashcards, skill_id=skill_id) 
 
    
    #Function sends the list of skills to the study timer so a 
#user can select which skill the alocated time will go towards.
# - opens database to retrieve skill list
#- GETs skill list and sends it 
@app.route("/focusTimer")
def focusTimer():
    #return render_template("studytimer.html")
    if "username" not in session:
        return redirect(url_for("login"))
    
    try: 
        with sqlite3.connect("database.db") as conn:
            cur = conn.cursor()
            query_1 = "SELECT uid FROM users WHERE username=?;"
            cur.execute(query_1, (session["username"],))

            row = cur.fetchone()
            if not row:
                return redirect(url_for("focusTimer"))
            user_id = row[0]
    
            query_2 = """SELECT  skill_id, name FROM skills WHERE user_id = ?;"""
            cur.execute(query_2, (user_id,))
                
            rows = cur.fetchall() 
            if not rows:
                return render_template("studytimer.html", skills_dict={})
                # returns tuples in a list so for ease before sending it to the js 
                # get just the list of skill names

            skills_dict = {} 
            # for ease stored as a dict 
            for row in rows: 
                skills_dict[row[0]] = row[1]
            return render_template("studytimer.html", skills_dict=skills_dict) 
        
    except sqlite3.Error:
        return render_template("studytimer.html", skills_dict={})

    
#TODO
 #Gets study duration from js, is a hidden post request
#that gets the info collected 

@app.route("/saveTimerStats", methods = ["POST"])
def saveTimerStats():

    if "username" not in session:
        return redirect(url_for("login"))
   
    data = request.get_json()
    skill_id = data.get('skill_id')
    timeSpent = data.get('time')

    timer_xp = 15

    if not skill_id or not timeSpent:
        return jsonify({"status": "data missing"})
    
    #TODO 
    # update database schema and add a new section for time spent for each skill
    # problably need to select find current time spend add on py and put back in
    # or maybe there is a way to just add to a value in sql  
    try:
        with sqlite3.connect("database.db") as conn:
            cur = conn.cursor() 
            query_1 = """UPDATE skills SET time_spent = time_spent + ? WHERE skill_id = ?; """
            cur.execute(query_1, (timeSpent, skill_id ))
            
            conn.commit()


            query_2 = "SELECT uid FROM users WHERE username=?;"
            cur.execute(query_2, (session["username"],))

            row = cur.fetchone()
            if not row:
                return redirect(url_for("focusTimer"))
            user_id = row[0]

            query_3 = """UPDATE users SET xp = xp + ?  WHERE uid = ?;"""
            cur.execute(query_3, (timer_xp, user_id))
            update_level(cur, user_id)
            conn.commit() 
            

    except sqlite3.Error:
        return jsonify({"status": "error"})

    return jsonify({"status": "complete"})


def update_level(cur, user_id):
    """"
    FUnction is called after successfully completing a quiz, study session, etc
    opens database to  updated xp (after a task) does a int divis
    to be put into the level column 
    """
    #NOTE:
    # xp should be updated in their under the function of that section 
    #this will open the database AFTER that update is done

    #TODO :
    # get xp and update level 
    
    query_1 = """SELECT xp, level FROM users WHERE uid = ?;"""
    cur.execute(query_1, (user_id,))
    row = cur.fetchone()
    if not row:
        return 
    
    xp = int(row[0])
    current_level = int(row[1])
    #just in case im using int

    level_ammount = 100 
    # 1 level = 100 xp (int divis)
    if xp >= level_ammount:
        level_earned = xp // level_ammount
        leftover_xp = xp % level_ammount



        query_2 = """UPDATE users SET level = level + ?, xp = ? WHERE uid = ?;"""
        cur.execute(query_2, (level_earned, leftover_xp, user_id) )

    else:
        return
   

if __name__=="__main__":
    app.run(debug=True)