document.addEventListener("DOMContentLoaded", function() {

  var socket = io(location.protocol + '//' + document.domain + ':' + location.port );
  var players = [];
  var leader = '';

  socket.on('connect', function() {
      socket.emit('first event', {data: 'I\'m connected!'});
  });


  if (join == 'False'){
    socket.emit('lobby join',{'room_creation':'True','username':username,'room_id':room_id});
  }
  else{
    socket.emit('lobby join',{'room_creation':'False','username':username,'room_id':room_id});
  }


//room chat + system messages:
  document.querySelector('#send_message').onclick = ()=> {
    socket.emit('lobby messages',{'msg':document.querySelector('#user_message').value,'username':username
  ,'room_id':room_id});
    document.getElementById('user_message').value = '';
  };

  //To send messages on pressing enter
  document.getElementById('user_message').addEventListener('keyup',function(e){
    if(e.keyCode == 13){
      document.getElementById('send_message').click();
    }
  });

  socket.on('lobby chat', data => {
    const p = document.createElement('p');
    p.innerHTML = data.username +' : ' + data.msg;
    p.setAttribute("class", "user-message-in-chatbox");
    document.querySelector("#msg-box").append(p);
  });

  function append_sys_msg_to_lobby_chat(x){   //this function appends whatever string given as parameter, to the msg box as a system message
    const p = document.createElement('p');
    p.innerHTML = x;
    p.setAttribute('class','sys-message-in-chatbox');
    document.getElementById('msg-box').append(p);
  }

  //function to update the connected users(when a users joins or leaves the room)
  function update_connected_users(x) {   //the object x is of the form : {event:join or leave,usr:johndoe}
    if(x.event == 'join'){
        players.push(x.usr);
        const p = document.createElement('p');
        p.innerHTML = '->' + x.usr ;
        p.setAttribute('class','users-connected');
        p.setAttribute('id','_' + x.usr + '_' );  //ids' are always like _saif_  so that theres no problem with other ids
        document.getElementById('users').append(p);
      }
    else{
      if(x.usr == leader+' (lobby leader)'){
        swal({
          title:'oops!',
          text:'Seems like the lobby leader has left the room...\n The game can only be started by the lobby leader.\nPlease return to the home page and create a new room or join one if you want to play',
          icon:'warning'
        });
      }

      var ps = document.getElementById('users').querySelectorAll('p');
      for(i=0;i<ps.length;i++){
        if(players[i] == x.usr){
          players.splice(i,1);
        }
        if(ps[i].id == '_' + x.usr + '_'){
          ps[i].remove();}
          }
        }
      }


//this part updates data for connected users as new users join or leave
  socket.on('room updates', data => {  //data object specs : {event:'create' or 'join' or 'leave',username:johndoe}
    if(data.event == 'create'){
      append_sys_msg_to_lobby_chat(data.username + ' has created a new room!');
      update_connected_users({event:'join',usr:data.username +' (lobby leader)' });
    }
    else if(data.event == 'join'){
      append_sys_msg_to_lobby_chat(data.username + ' has joined the room!');
      update_connected_users({event:'join',usr:data.username });
    }
    else{
      append_sys_msg_to_lobby_chat(data.username + ' has left the room.');
      update_connected_users({event:'leave',usr:data.username });
    }
  });
  
//data about existing users in the room for the new user
  socket.on('clients_info', data =>{
    leader = data.leader;
    for(i=0;i<data.arr.length;i++)    //this updates the connected users for the newly joined user
     {
       update_connected_users({event:'join',usr:data.arr[i]});
     }

  });


//event handler function when players leave 
function left() {
  socket.emit('leaving lobby',{'username':username,'room_id':room_id});
}

window.addEventListener("beforeunload", left);

//to start the game
try{
      document.querySelector('#start-button').onclick = ()=> {
        if(players.length > 1){
          socket.emit('game-start' , room_id);
          window.removeEventListener("beforeunload",left);
          document.getElementById("start-request").submit();}
        else{
          swal({
            title:'oops!',
            text:'At least two players have to be in a room to start the game!',
            icon : 'warning'
          });
        }
      };
}
catch(err){}


socket.on('game start',data => {
    window.removeEventListener("beforeunload",left);
    socket.emit('remove from room',room_id);
    document.getElementById("start-request").submit();
  });


});