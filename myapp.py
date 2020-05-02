import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import os
import numpy as np
import orjson

import redis
r = redis.from_url(os.environ.get('REDIS_URL'), charset = 'utf-8', decode_responses = True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
socketio = SocketIO(app)

def gen_roomid():
    while True:
        roomID = ''
        for i in range(6):
            roomID += str(random.randint(1, 9))
        if(r.exists(roomID) == 0):
            return roomID

def change_rooms_dict_value_per_key(dt, ri):  #'d' is the simple dict and this func. changes the roomid value(dict) into complex dict for given roomid(key)
    x = dt['users'].copy()
    dt['users'] = { i:[] for i in x }
    r.set(ri, orjson.dumps(dt).decode('utf-8'))  #storing changes on db as a json string

def add_dict_to_a_user(user, ri, dt): # only adds dict where k:v are different possibilities of a user getting a point , for eg.: {row1:Flase,row2:True}...which means row2 point has been calculated
    l = ['row' + str(i) for i in range(1, 6)] + ['col' + str(i) for i in range(1, 6)] + ['diag1', 'diag2']
    scores_possibilities = { k:False for k in l }
    dt['users'][user].append(scores_possibilities)
    r.set(ri, orjson.dumps(dt).decode('utf-8'))


def button_click_updation(dt, ri, x): #dt is the value of roomid key in db, x is button clicked , ri is room_id
    d = dt['users']
    for i in d: #dt has keys 'users' and 'started' and d['users'] is of the format {'user1':[list_obj],'user2':[list_obj]....}
        if isinstance(d[i], list):
            l = d[i].copy() #copy of order of a user with dict
            l.pop(-1) #pops the dict as its the last element
            l = np.array(l)
            t = np.argwhere( l == int(x))[0]  #returns a 2d list containing the coordinates of x and since its a 2d list with only one element which is also a list, '[0]' is used
            d[i][t[0]][t[1]] = 77 # t has values like [x-coordinate,y-coordinate] (of button clicked), hence using it to access that clicked button
            #that value 77 could be anything but it must be a number and shouldnt be the (1,26) range
            #its because numbers make it easier to work with numpy and that number(in this case 77) means that button is clicked... thats it
    r.set(ri, orjson.dumps(dt).decode('utf-8'))

def check_for_points(dt, ri): #returns a dict with username as keys and their score as values(if any) and d keys value pairs as username:list in a particular room
    rd = {} #result dict
    d = dt['users']

    for i in d:
        if isinstance(d[i], list): #checking because after a player has finished game, their value becomes 'Finished'
            pts = 0
            l = d[i].copy() #copy of order of a user with dict
            l.pop(-1) #pops the score tracker dict as its the last element
            l = np.array(l)
            scores = d[i][-1] #that users dict which says the different points that have been allotted (True if allotted, else False)
            for way in scores: #way as in different ways to score a point like row1 or daig2 and so on
                if not scores[way]: #that way's value is False if that point is not yet allotted and if its allotted then no need to calculate
                    if way[0] == 'r' and len(set(l[int(way[-1]) - 1])) == 1: #keys in 'scores' dict are 'row1','col1'..etc, way[0] says if its a row or column or diagonal we re dealing with and way[-1] is the char such as '1','4' etc
                        pts += 1   #if that row is filled,player gets one point
                        scores[way] = True
                    elif way[0] == 'c' and len(set(l[: , int(way[-1]) - 1])) == 1: #different ways to check for diff possibilities , hence for column different computation is done
                        pts += 1
                        scores[way] = True
                    elif (way[0] =='d' and way[-1] == '1') and len(set(np.diagonal(l))) == 1: #to check if values are filled in primary diagonal
                        pts += 1
                        scores[way] = True
                    elif (way[0] == 'd' and way[-1]=='2') and len(set(np.diag(np.fliplr(l)))) == 1: # for the other diagonal
                        pts += 1
                        scores[way] = True
            if pts != 0:
                rd[i] = pts

    if len(rd) != 0:
        r.set(ri, orjson.dumps(dt).decode('utf-8'))
        return rd
    return 0

def check_if_game_finished(d, ri):  #only dict at value 'users' in roomid in db, is enough here as no changes are made to db
    if len(d) == 1:       #if only one player is playing then the game is force stopped...might happen if players left during rearranging time and only one player is playing
        emit('force stop', True, room=ri)
        r.delete(ri)
    else:
        l = list(d.values())
        if l.count('Finished') == len(l) - 1:
            r.delete(ri)
            emit('game finished', 'True', room = ri)
            return True
        return False

def check_if_all_players_ready(ri, dt):
    if len(dt['joined_game']) == len(dt['users']):
        emit('players ready', True, room = ri)
        dt.pop('joined_game', None)
        r.set(ri, orjson.dumps(dt).decode('utf-8'))

@app.route('/')
@app.route('/home')
def f1():
    query_params = request.args

    if 'create' in query_params and 'join' in query_params:
        return '<h1>Hey smartass! It won\'t work xD</h1>'
    if 'create' in query_params:
        return render_template('home.html', title = 'Bingo! | Play Bingo online with friends', create = True)
    if 'join' in query_params:
        return render_template('home.html', title = 'Bingo! | Play Bingo online with friends', join = True)

    return render_template('home.html', title = 'Bingo! | Play Bingo online with friends')

@app.route('/lobby',methods=['GET','POST'])
def f2():
    if request.method == 'GET':
        return redirect(url_for('f1'))

    if 'room_id' in request.form:
        if r.exists(request.form['room_id']) == 1:
            ri = request.form['room_id']
            usr = request.form['username']
            d = orjson.loads(r.get(ri))

            if d['started']:
                return '<h1>The game has started in this rooom!</h1><h2>You cannot join this room anymore. Please create a new room or join another one</h2>'
            if usr in d['users']:
                return render_template('home.html', title = 'Bingo! | Play Bingo online with friends',join = True, user_already_exists =True)
            if len(d['users']) < 7:
                d['users'].append(usr)
                r.set(ri, orjson.dumps(d).decode('utf-8'))
            else:
                return '<h1>Sorry! This room is full! Try joining another room or create new one</h1>'

            return render_template('lobby.html',title = 'Bingo! | lobby',username = usr,room_id = ri,join = True)
        return '<h1>Invalid room id</h1>'

    room_id = gen_roomid()
    usr = request.form['username']
    s = orjson.dumps({ 'users': [usr], 'started': False}).decode('utf-8')
    r.set(room_id, s)
    r.expire(room_id, 60 * 60)

    return render_template('lobby.html', title = 'Bingo! | lobby', username = usr, room_id = room_id, join = False)

@app.route('/game',methods = ['POST'])
def f3():
    if request.method == 'GET':
        return redirect(url_for('f1'))

    data = request.form
    usr = data['username']
    ri = data['room_id']

    if r.exists(ri) == 1:
        dt = orjson.loads(r.get(ri))
        d = dt['users']
        if usr in d:
            if data['rearranged'] == 'False':
                return render_template('game.html', title = 'Bingo! | game', rearranged = False, username = usr, room_id = ri, join = eval(data['join']))

            l = [j for i in d[usr] for j in i]
            add_dict_to_a_user(usr, ri, dt) #dt is the json-to-python converted dict, passed to save computations
            return render_template('game.html', title = 'Bingo! | game', rearranged = True, username = usr, room_id = ri, order = l, join = eval(data['join']))

        return '<h1>Please either create or join a room and then start the game</h1>'
    return '<h1>Please either create or join a room and then start the game</h1>'

@app.route('/about')
def about():
    return render_template('about.html' ,title = 'Bingo! | About')

@socketio.on('first event')
def handler(h):
    print('\n this is my msg: recieved!! \n')

@socketio.on('lobby join')
def on_join(data):
    ri = data['room_id']
    usr = data['username']
    join_room(ri)

    if data['room_creation'] == 'True':
        return emit('room updates', {'event': 'create', 'username': usr}, room = ri)

    d = orjson.loads(r.get(ri))
    x = d['users'].copy()
    x.pop(-1)
    ll = x[0]  #ll for lobby leader
    x[0] += ' (lobby leader)'
    emit('room updates', {'event': 'join', 'username': usr}, room = ri) #update data as an incoming user to already connected users
    emit('clients_info', {'leader': ll, 'arr': x})  #data about the already existing users in the room for the new user, which is a list of usernames in the room except the new user

@socketio.on('lobby messages')
def handle_message(data):
    emit('lobby chat', {'msg': data['msg'], 'username': data['username']}, room = data['room_id'])

@socketio.on('leaving lobby')
def leave(data):
    usr = data['username']
    ri = data['room_id']
    leave_room(ri)
    if r.exists(ri) == 1:
        dt = orjson.loads(r.get(ri))
        d = dt['users']
        if usr == d[0]:
            emit('room updates', {'event': 'leave', 'username': usr + ' (lobby leader)'}, room = ri)
            r.delete(ri)
        else:
            d.remove(usr)
            r.set(ri, orjson.dumps(dt).decode('utf-8'))
            emit('room updates', {'event': 'leave', 'username': usr}, room = ri)

@socketio.on('game-start')
def start(ri):  #ri is the room id
    dt = orjson.loads(r.get(ri))
    dt['started'] = True
    r.set(ri, orjson.dumps(dt).decode('utf-8'))
    emit('game start', 'True', room = ri)

@socketio.on('remove from room')
def remove(x):
    leave_room(x)

@socketio.on('joined first game page')
def game_join(data):
    ri = data['room_id']
    join_room(ri)
    d = orjson.loads(r.get(ri))
    emit('players', d['users'])

@socketio.on('new order')
def order(data):
    ri = data['room_id']
    user = data['username']
    dt = orjson.loads(r.get(ri))
    d = dt['users']

    if isinstance(d, list):
        change_rooms_dict_value_per_key(dt, ri)
        dt = orjson.loads(r.get(ri))  #get updated values
        d = dt['users']

    l = list(map(int, data['order'])) #user order of buttons
    l = [l[i:i+5] for i in range(0, 21, 5)] #to convert it into a 2d list

    if len(d[user]) == 0:
        d[user].extend(l)
        r.set(ri, orjson.dumps(dt).decode('utf-8')) #saving changes in db

@socketio.on('left first game page')
def kick1(data):
    usr = data['username']
    ri = data['room_id']
    if r.exists(ri) == 1:
        dt = orjson.loads(r.get(ri))
        dt['users'].remove(usr)
        r.set(ri, orjson.dumps(dt).decode('utf-8'))

@socketio.on('joined second game page')
def joined_second(data):
    ri = data['room_id']
    usr = data['username']
    join_room(ri)
    dt = orjson.loads(r.get(ri))
    if 'joined_game' not in dt:
        dt['joined_game'] = []
    dt['joined_game'].append(usr)
    emit('players', list(dt['users'].keys()))
    r.set(ri,orjson.dumps(dt).decode('utf-8'))
    check_if_all_players_ready(ri, dt)  #when all are ready, message will be sent to all clients in the room and then only post request for 2nd game page will be made

@socketio.on('user-turn')   #event bucket to tell whos turn it is next and to handle the button clicks made by the users/ update scores
def turn(data):
    usr = data['username'] #username of player who just clicked a button
    ri = data['room_id']
    if r.exists(ri) == 1:  #in case some message is recieved after room is deleted
        dt = orjson.loads(r.get(ri))   #d is of the form {'user1':list,'user2':list...}
        d = dt['users']
        if not check_if_game_finished(d,ri):  #if yes,the room_id is popped off the db and a message is emitted to clients in the room saying game is finished
            x = data['button-clicked']
            button_click_updation(dt, ri, x) #updates for all users
            dt = orjson.loads(r.get(ri)) #pull latest values from db
            d = dt['users']
            pts = check_for_points(dt, ri) #returns a dict with 'usernames':point as k:v pairs ,if any and returns 0 if there are no updates in points
            l = [i for i in d if isinstance(d[i], list)] #for players who have finished, their values become 'Finished', hence checking if values are list instances
            nt = l.index(usr) + 1 if usr != l[-1] else 0 #index of user who is supposed to play the next turn
            data = {'currentuser': l[nt], 'disable': str(x)}
            if pts != 0 :
                emit('score update', pts, room = ri)
            emit('current turn', data, room = ri)

@socketio.on('left second game page')
def kick2(data):
    usr = data['username']
    ri = data['room_id']
    if r.exists(ri) == 1:
        dt = orjson.loads(r.get(ri))
        l = list(dt['users'].keys()) #list of users playing(including the one who left)
        dt['users'].pop(usr, None)
        r.set(ri, orjson.dumps(dt).decode('utf-8'))
        if len(dt['users']) == 1: #if only one player is playing then the game is force stopped
            emit('force stop', True, room = ri)
            r.delete(ri)
        elif data['current_turn']: #if the (current)player leaves the game, then the roundrobin has to be adjusted:
            nt = l.index(usr) + 1 if usr != l[-1] else 0 #index of user who is supposed to play the next turn
            emit('current turn', {'currentuser': l[nt]}, room = ri)
        emit('player left', {'username': usr}, room = ri)

@socketio.on('player finished')
def finished(data):
    usr = data['username']
    ri = data['room_id']
    if r.exists(ri) == 1:
        dt = orjson.loads(r.get(ri))
        d = dt['users']
        d[usr] = 'Finished'
        r.set(ri, orjson.dumps(dt).decode('utf-8'))
        check_if_game_finished(d,ri)

if __name__ == '__main__':
    socketio.run(app, host=os.environ.get('APP_HOST'), port=os.environ.get('APP_PORT'))
