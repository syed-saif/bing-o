document.addEventListener("DOMContentLoaded", function() {

  var socket = io(location.protocol + '//' + document.domain + ':' + location.port );

  socket.on('connect', function() {
      socket.emit('first event', {data: 'I\'m connected!'});
  });

  document.getElementById('rules').onclick = () =>{
    swal({
    title: "Here's out it works",
    text: "1.Before the game starts the players get 1 minute to re-arrange the numbers in the order they wish.\n2.After the time has elapsed, each player will get a turn to click one button(or number).\n3.A button can be clicked only once and cannot be used again.\n4.On each turn, the clicked button will be disabled to all the players in the game.\n5.After a number of turns, when either a row or a column or a diagonal of buttons are clicked for a player, they are awarded one point.\n6.The first player to score 5 points, wins!\n(B-I-N-G-O!! , where each letter denotes a point).   ",
    button: {
        text: "GOT IT!",
      icon : "info",
      closeModal: true,
          }
      });
  };

  try{
    document.getElementById('btnsubmit').onclick = () =>{
      if(document.getElementById('username').value.trim().length == 0){
        swal({
          title: "oops!!",
          text: "The username field cannot be empty.Please fill in proper values.",
          icon:"warning"
        });
      }
      else{
        document.getElementById('home-form').submit();
      }
    };
    document.getElementById('ri').addEventListener('keyup',function(e){
      if(e.keyCode == 13){
        document.getElementById('btnsubmit').click();
      }
    });

   }
   catch{}

   window.addEventListener("beforeunload", function(e) {
     socket.emit('test','\nemit fired before page was closed\n');
   });


});
