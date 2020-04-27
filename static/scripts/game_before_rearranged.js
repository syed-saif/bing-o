document.addEventListener("DOMContentLoaded", function() {

  var socket = io(location.protocol + '//' + document.domain + ':' + location.port );
  var timer = new Timer();

  socket.on('players', data => {
    for(i=0;i<data.length;i++){
      const p = document.createElement('p');
      p.innerHTML = data[i] + ' : ';
      document.getElementById('score-board').append(p);
    }
  });

  socket.emit('joined first game page',{'room_id':room_id});

  //event handler function when players leave 
  function left() {
    socket.emit('left first game page',{'username':username,'room_id':room_id});
  }

  window.addEventListener("beforeunload", left);


  //This event is triggered when countdown timer ends....
  timer.addEventListener('targetAchieved' ,function (e) {
      window.removeEventListener("beforeunload", left);
      $('#timer .values').html('game starting..');          //form is submitted once time ends and game starts
      var l = grid.getItems().map(item => item.getElement().getAttribute('data-id'));
      socket.emit('new order',{'username':username,'room_id':room_id,'order':l});
      socket.emit('remove from room',room_id);
      document.getElementById("rearranged").submit();    
  });

 //first pop up saying the players to rearrange
  window.setTimeout( () => {
    swal({
      title:'Attention!',
      text:'You have one minute to re-arrange the buttons in the order you want.',
      icon:'warning',
      closeOnClickOutside: false,
      button: false,
      timer:2000
    }).then( () => {       //as soon as popup closes, timer starts:
        timer.start({countdown:true,startValues:{minutes:1,seconds:30}});
        timer.addEventListener('secondsUpdated', function (e) {
            $('#timer .values').html(timer.getTimeValues().toString());
        });
    });
  },1000);

  
  
});
