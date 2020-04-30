document.addEventListener("DOMContentLoaded", function() {

  var socket = io(location.protocol + '//' + document.domain + ':' + location.port );
  var scores = {};
  var ll = ''; //lobby leader's name
  var positions = []; //all players' position when game ends ....(players' name are pushed into array as they finish )
  var finished = false; //to stop all functionalities once game finishes
  var isTheirCurrentTurn = false; //used to check if the this player has to play currently; used in beforeunload event

  socket.emit('joined second game page',{'username':username,'room_id':room_id});

  function update_current_turn(user){
    if(user == username){
    document.getElementById('ct').innerHTML = "Current turn: It's your turn!";}
    else{document.getElementById('ct').innerHTML = 'Current turn: '+ user;}
  }

  socket.on('players' , data => {
      ll = data[0];
      for(i=0;i<data.length;i++){
        scores[data[i]] = 0;
        const p = document.createElement('p');
        p.innerHTML = data[i]+' : ';
        p.setAttribute('id',data[i]);
        document.getElementById('score-board').append(p);
      }
  });

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


//event handler function when players leave
  function left() {
    socket.emit('left second game page',{'username':username,'room_id':room_id,'current_turn':isTheirCurrentTurn});
  }

  window.addEventListener("beforeunload", left);


//
  function reset_btns(x){
    socket.emit('user-turn',{'username':username,'room_id':room_id,'button-clicked':x});
    }

  function allow_click(){

    $('button.bingo-btns').on('click',function(){
    $(this).prop('disabled' , 'true') ; //because buttons can be clicked only once
    $(this).attr('style', 'cursor:not-allowed;');
    $(this).removeClass('btn-danger').addClass('btn-light'); //changes the button color to light indicating that the button is used and can no longer be used
    reset_btns($(this).text());
    $('button.bingo-btns').off('click');
    isTheirCurrentTurn = false;
    });

  }

  append_sys_msg_to_lobby_chat("Waiting for players..");

  socket.on('players ready', data => {
    update_current_turn(ll);
    append_sys_msg_to_lobby_chat("Game started!");
    if(join == "False"){ //only be true for lobby leader
        allow_click();
      }

  });

  socket.on('current turn', data => {
    isTheirCurrentTurn = true;
    if(data.hasOwnProperty('disable')){
        $('[data-id=' + data.disable +']').prop('disabled' , 'true') ;
        $('[data-id=' + data.disable +']').attr('style', 'cursor:not-allowed;').removeClass('btn-danger').addClass('btn-light');
        update_current_turn(data.currentuser);
      }
    if(data.currentuser == username && !(finished)){
      allow_click();
    }
  });

  socket.on('score update', data => {
    var arr = ['B','-I','-N','-G','-O!!'];
    for(var user in data) {
      if(data.hasOwnProperty(user)){
         const t = scores[user];
         scores[user] += data[user];
         if(scores[user] == 5){        //as soon as one player finishes their name is pushed to 'positions' array in all the clients
          positions.push(user);
          if(user==username){   //only for that client , a socket message is emitted(to save network calls) and finished prompt is displayed
             socket.emit('player finished',{'username':user,'room_id':room_id});
             const p = document.createElement('p'); p.innerHTML = 'You have finished! Waiting for others to finish...';
             document.getElementById('finished').append(p);}
         }
         document.getElementById(user).innerHTML += arr.slice(t,scores[user]).join('') ;
        }
      }
  });

  socket.on('player left', data => {
    const usr = data.username
    append_sys_msg_to_lobby_chat( usr + " has left the game");
    $('#' + usr).remove();
  });

  socket.on('game finished', data => {
    finished = true;

    $('#finished').empty();
    $('#finished').html("<p><b>You have finished!</b><br>Waiting for other to finish...</p>");

    for(player in scores){
      if(scores.hasOwnProperty(player)){
        if( positions.indexOf(player)==-1){
          positions.push(player);
        }
      }
    }
    txt = "Positions: \n";
    for(i=0;i<positions.length;i++){
      txt +=  "No."+ String(i+1) + " : " + positions[i] + "\n";
    }
    txt += "You will be redirected to home page in a few moments..";
    swal({
      title : 'BINGO!! Game finished!',
      text: txt,
      icon:'success',
      button: false,
      closeOnClickOutside: false,
      closeOnEsc: false,
      timer:17000,
    }).then(() => {
      window.removeEventListener("beforeunload", left);
      window.location.replace('/home');
    });
  });

  socket.on('force stop', data => {    //when players leave the game and only one is left, the game is force stopped
    finished = true;
    swal({
      title:'oops!!',
      text: "Seems like others left and you're the only one playing!! \n Since the game needs at least two people to play, you can no longer continue this game. \nYou will be redirected to home page in a few seconds.." ,
      icon:'warning',
      button: false,
      closeOnClickOutside: false,
      closeOnEsc: false,
      timer:13000
      }).then(() => {
        window.removeEventListener("beforeunload", left);
        window.location.replace('/home');
      });
  });




});
