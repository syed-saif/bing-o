document.addEventListener("DOMContentLoaded", function() {

  var socket = io(location.protocol + '//' + document.domain + ':' + location.port );
  var scores = {};
  var ll = ''; //lobby leader's name
  var positions = []; //all players' position when game ends ....(players' name are pushed into array as they finish )
  var finished = false; //to stop all functionalities once game finishes

  socket.emit('joined second game page',room_id);

  function update_current_turn(user){
    if(user == username){
    document.getElementById('ct').innerHTML = "It's your turn!";}
    else{document.getElementById('ct').innerHTML = user;}
  }

  socket.on('players' , data => {
      ll = data[0];
      update_current_turn(ll);
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

    append_sys_msg_to_lobby_chat("Game started!");

//
  function reset_btns(x){
    socket.emit('user-turn',{'username':username,'room_id':room_id,'button-clicked':x});
    }

function allow_click(){

  $('button.bingo-btns').on('click',function(){
  $(this).prop('disabled' , 'true') ;
  $(this).attr('style', 'cursor:not-allowed;');
  reset_btns($(this).text());
  $('button.bingo-btns').off('click');
  });
}



  if(join == "False"){ //only be true for lobby leader
    allow_click();
  }


  socket.on('current turn', data => {

    $('[data-id=' + data.disable +']').prop('disabled' , 'true') ;
    $('[data-id=' + data.disable +']').attr('style', 'cursor:not-allowed;');
    update_current_turn(data.currentuser);
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
         if(scores[user] == 5 && user==username){
           socket.emit('player finished',{'username':user,'room_id':room_id});
           positions.push(user);
           const p = document.createElement('p'); p.innerHTML = 'You have finished! Waiting for others to finish...';
           document.getElementById('finished').append(p);
         }
         document.getElementById(user).innerHTML += arr.slice(t,scores[user]).join('') ;
        }
      }
  });


  socket.on('game finished', data => {
    finished = true;

    const p = document.createElement('p'); p.innerHTML = "Game has finished, please return to home page to play a new game."
    document.getElementById('finished').append(p);

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
      timer:15000,
    }).then(() => {
      window.location.replace('/home');
    });
  });

});
