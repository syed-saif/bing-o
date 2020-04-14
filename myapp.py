from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import numpy as np
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
socketio = SocketIO(app)

rooms = {}  #initially, keys are room_id and values are lists of users in that room


def gen_roomid():
    s = ''
    for i in range(6):
        s += str(random.randint(1,9))
    return s


def change_rooms_dict_value_per_key(ri):  #changes the rooms dict into complex dict for given key
    x = list(rooms[ri])
    rooms[ri]={i:[] for i in x}


def convert_list_of_users_to_a_tuple(ri): #To ensure that nobody joins the lobby once the game has started, the list of users becomes a tuple as soon as first game page is loaded
    rooms[ri]=tuple(rooms[ri])


def add_dict_to_a_user(user,ri): # only adds dict where k:v are different possibilities of a user getting a point , for eg.: {row1:Flase,row2:True}...which means row2 point has been calculated
    l = ['row'+str(i) for i in range(1,6)] + ['col'+str(i) for i in range(1,6)] + ['diag1','diag2']
    d = {k:False for k in l}
    rooms[ri][user].append(d)


def button_click_updation(ri, x): #x is button clicked , ri is room_id
    for i in rooms[ri]:
        if isinstance(rooms[ri][i],list):
            l = rooms[ri][i].copy() #copy of order of a user with dict
            l.pop(-1) #pops the dict as its the last element
            l = np.array(l)
            t = np.argwhere( l == int(x))[0]  #returns a 2d list containing the coordinates of x and since its a 2d list with only one element which is also a list, '[0]' is used
            rooms[ri][i][t[0]][t[1]] = 77 # t has values like [x-coordinate,y-coordinate] (of button clicked), hence using it to access that clicked button
            #that value 77 could be anything but it must be a number and shouldnt be the (1,26) range
            #its because numbers make it easier to work with numpy and that number(in this case 77) means that button is clicked... thats it

def check_for_points(ri): #returns a dict with username as keys and their score as values(if any)
    rd = {} #result dict
    for i in rooms[ri]:
        if isinstance(rooms[ri][i],list):
            pts = 0
            l = rooms[ri][i].copy() #copy of order of a user with dict
            l.pop(-1) #pops the score tracker dict as its the last element
            l = np.array(l)
            d = rooms[ri][i][-1] #that users dict which says the different points that have been allotted (True if allotted, else False)
            for way in d: #way as in different ways to score a point like row1 or daig2 and so on
                if not d[way]: #that way's value is False if that point is not yet allotted and if its allotted then no need to calculate
                    if way[0]=='r' and len(set(l[int(way[-1]) - 1])) == 1: #way[-1] is the char such as '1','4' etc
                        pts += 1
                        d[way] = True
                    elif way[0]=='c' and len(set(l[: , int(way[-1]) - 1])) == 1:
                        pts += 1
                        d[way] = True
                    elif (way[0] =='d' and way[-1] == '1') and len(set(np.diagonal(l))) == 1:
                        pts += 1
                        d[way] = True
                    elif (way[0]=='d' and way[-1]=='2') and len(set(np.diag(np.fliplr(l)))) == 1:
                        pts += 1
                        d[way] = True
            if pts != 0:
                rd[i] = pts
    return rd if len(rd)!=0 else 0

def check_if_game_finished(ri):
    l = list(rooms[ri].values())
    if l.count('Finished') == len(l)-1:
        print("\ngame fiinished\n")
        rooms.pop(ri , None)
        emit('game finished',  'True' ,room = ri)
        return True
    return False

@app.route('/')
@app.route('/home')
def f1():
    query_params = request.args
    if 'create' in query_params and 'join' in query_params:
        return "<h1>Hey smartass! It won't work xD</h1>"
    if 'create' in query_params:
        return render_template("home.html", title = "test app",create = True)
    if 'join' in query_params:
        return render_template("home.html", title = "test app",join = True)
    return render_template("home.html", title = "test app")

@app.route('/lobby',methods=['GET','POST'])
def f2():
    if request.method == 'GET':
        return "<h1>Please either create a room or join a room!</h1>"
    else:
        if 'room_id' in request.form:
            if request.form['room_id'] in rooms:
                ri = request.form['room_id']
                usr = request.form['username']
                if isinstance(rooms[ri],tuple):
                    return "<h1>The game has started in this rooom!</h1><h2>You cannot join this room anymore. Please create a new room or join another one</h2>"
                if len(rooms[ri]) < 7:
                    rooms[ri].append(usr)
                else:
                    return "<h1>Sorry! This room is full! Try joining another room or create new one</h1>"
                return render_template("lobby.html",title = "game lobby",username = usr,room_id = ri,join = True )
            else:
                return "<h1>Invalid room id</h1>"
        room_id = gen_roomid()
        usr = request.form['username']
        rooms[room_id] = [usr]
        return render_template("lobby.html",title = "game lobby",username = usr,room_id = room_id , join = False)

@app.route('/game',methods=['POST'])
def f3():
    d = request.form
    usr = d['username']
    ri = d['room_id']
    if ri in rooms and usr in rooms[ri]:
        if d['rearranged'] == 'False':
            return render_template("game.html",title ="game",rearranged=False,username = usr,room_id=ri,join = eval(d['join']))
        else:
            l = [j for i in rooms[ri][usr] for j in i]
            add_dict_to_a_user(usr,ri)
            return render_template("game.html",rearranged=True,username = usr,room_id=ri,order = l,join=eval(d['join']))
    else:
        return "<h1>Please either create or join a room and then start the game</h1>"

@app.route('/test')
def f4():
    return render_template("sweetalerttest.html")

@socketio.on('test')
def test(msg):
    print(msg)


@socketio.on('first event')
def handler(h):
    print("\n this is my msg: recieved!! \n")

@socketio.on('lobby join')
def on_join(data):
    join_room(data['room_id'])
    if data['room_creation'] == 'True':
        emit('room updates',{'event':'create','username':data['username']},room=data['room_id'])
    else:
        x = rooms[data['room_id']].copy()
        usr = data['username']
        x.pop(-1)
        ll = x[0]  #ll for lobby leader
        x[0] += ' (lobby leader)'
        emit('room updates',{'event':'join','username':data['username']},room=data['room_id']) #update data as an incoming user to already connected users
        emit('clients_info',{'leader':ll,'arr':x})  #data about the already existing users in the room for the new user, which is a list of usernames in the room except the new user

@socketio.on('lobby messages')
def handle_message(data):
    emit('lobby chat', {'msg':data['msg'],'username':data['username']},room=data['room_id'])


@socketio.on('leaving lobby')
def leave(data):
    usr = data['username']
    ri = data['room_id']
    leave_room(ri)
    if usr == rooms[ri][0]:
        emit('room updates',{'event':'leave','username':usr+' (lobby leader)'},room=ri)
        rooms.pop(ri,None)
    else:
        rooms[ri].remove(usr)
        emit('room updates',{'event':'leave','username':usr} ,room = ri)

@socketio.on('game-start')
def start(x):  #x is the room id
    emit('game start','True', room = str(x))

@socketio.on('remove from room')
def remove(x):
    leave_room(x)


@socketio.on('joined first game page')
def game_join(data):
    ri = data['room_id']
    join_room(ri)
    if isinstance(rooms[ri],list):
        convert_list_of_users_to_a_tuple(ri)
    emit('players', list(rooms[ri]))

@socketio.on('new order')
def order(data):
    ri = data['room_id']
    user = data['username']
    if isinstance(rooms[ri],tuple):
        change_rooms_dict_value_per_key(ri)
    l = list(map(int,data['order'])) #user order of buttons
    l = [l[i:i+5] for i in range(0,21,5)]
    if len(rooms[ri][user])==0:
        rooms[ri][user].extend(l)


@socketio.on('joined second game page')
def joined_second(room_id):
    join_room(room_id)
    emit('players', list(rooms[room_id].keys()))


@socketio.on('user-turn')   #event bucket to tell whos turn it is next and to handle the button clicks made by the users/ update scores
def turn(data):
    usr = data['username']
    ri = data['room_id']
    if ri in rooms:  #in case some message is recieved after room is deleted
        x = data['button-clicked']
        if  not check_if_game_finished(ri):  #if yes,the room_id is popped off the rooms dict and a message is emitted to clients in the room saying game is finished
            button_click_updation(ri , x) #updates for all users
            pts = check_for_points(ri) #returns a dict with 'usernames':point as k:v pairs ,if any and returns 0 if there are no updates in points
            l = [i for i in rooms[ri] if isinstance(rooms[ri][i],list)] #for players who have finished, their values become 'Finished', hence checking if values are list instances
            nt = l.index(usr) + 1 if usr != l[-1] else 0 #index of user who is supposed to play the next turn
            data = {'currentuser':l[nt],'disable':str(x)}
            if pts != 0 :
                emit('score update',pts,room = ri)
            emit('current turn',data,room=ri)

@socketio.on('player finished')
def finished(data):
    usr = data['username']
    ri = data['room_id']
    if ri in rooms:
        rooms[ri][usr] = 'Finished'
        check_if_game_finished(ri)



if __name__ == '__main__':
    app.run()
