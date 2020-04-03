import numpy as np
from flask import Flask, request, redirect, url_for,make_response,render_template_string
import random
import time
import json
import os
cwd=os.getcwd()

with open(cwd+"/data.json","r") as f:
    words=json.load(f)

print(words)

game={
    "player": [],
    "ready": [], 
    "fake": ""
}
maxPlayer=3
app = Flask(__name__)
startingGame=False
t1=0
new_word=""
restart=True

@app.route('/waiting_room')
def waiting_room():
    global startingGame,game,t1,new_word,restart
    

    pagecontent="""
    <h1>Waiting...</h1> Currently there are {}/{} ready:     
    <meta http-equiv="refresh" content="5">""".format(len(game["ready"]),maxPlayer)
    for p in game["player"]:
        if p in game["ready"]:
            pagecontent= pagecontent+"""<font color="green"> {} </font>""".format(p)
        else:
            pagecontent= pagecontent+"""<font color="red"> {} </font>""".format(p)


    if len(game["ready"])==maxPlayer and startingGame is False:
        startingGame=True
        #game is starting
        all_player=game["player"]
        game["fake"]=random.choice(all_player)
        all_words=words["words"]
        new_word=random.choice(all_words)
        print("Word: ", new_word)
        game["ready"]=[]
        restart=False
        print(game)
        t1=time.time()

    if startingGame==True and time.time()-t1>0.1:
        time.sleep(0.1)
        return redirect(url_for("own_page"))

    me=request.cookies.get("id")
    if (me not in game["player"] or me not in game["ready"]) and startingGame == False:
        print("not suposed to sit in waiting room:  ", me )   
        return redirect(url_for("join_game"))

    return pagecontent

@app.route("/restart",methods=["POST","GET"])
def starting_page():
    global startingGame,game,new_word,restart
    
    if request.method=="POST":
        game["player"]=[]
        game["ready"]=[]
        game["fake"]=""
        new_word=""
        restart=True
        return redirect(url_for("join_game"))

    return """
    <form method= POST>
    Restart <input type="submit">
    </form>    
    """

@app.route("/ready", methods=["POST","GET"])
def ready_game():
    global startingGame,game
    me=request.cookies.get("id")
    if request.method == "POST":
        if me in game["player"]:
            game["ready"].append(me)
            print(game)
            #return "<h2> Player name is {} </h2>".format(player)
            return redirect(url_for("waiting_room"))
        else:
            return redirect(url_for("join_game"))

    return """
    <h1> {} are you ready?  </h1>
    <form method="POST">
    Ready? <input type= "submit">
    </form>
    """.format(me)

@app.route("/", methods=["POST","GET"])
def join_game():
    global startingGame,game
    me = request.cookies.get("id")
    if me is not None:
        if me in game["player"]:
            return redirect(url_for("ready_game"))
        else:
            if me in game["player"]:
                return "<h1>Name already taken</h1>"
            else:
                game["player"].append(me)
                print(game)
                return redirect(url_for("ready_game"))

    if request.method == "POST":
        player= request.form.get("player")
        resp = make_response(redirect(url_for("join_game")))
        resp.set_cookie("id", player)
        print(game)
        #return "<h2> Player name is {} </h2>".format(player)
        return resp

    return """ <h1> Type your name here to join </h1>
    <form method="POST">
    Name <input type = "text" name="player">
    <input type= "submit">
    </form>
    """

@app.route("/own_page", methods=["POST","GET"])
def own_page():
    global startingGame,game,new_word
    me=request.cookies.get("id")
    
    if request.method=="POST":
        startingGame=False
        game["ready"].append(me)
        print(game)
        return redirect(url_for("waiting_room"))
    
    if restart == True:
        return redirect(url_for("join_game"))

    if me==game["fake"]:
        #role="a Fake"

        return """
        <h1> {}, du bist ein Fake!</h1>

        <form method= POST>
        New Round <input type="submit">
        </form> 

        """.format(me)
    else:
        return """
        <h1> {}, das ist das geheime Wort:  </h1>

        <h2>Wort: {} </h2> 

        <form method= POST>
        New Round <input type="submit">
        </form> 

        """.format(me,new_word)
    
    

if __name__ == "__main__":
    app.debug=True
    app.run(host='192.168.2.110',port=5005)

