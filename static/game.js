$(document).ready(function() {
    // Connect to server
    namespace = '/test';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    
    // Setup canvas
    var canvas = document.getElementById('canvas');
    var ctx
    if (canvas.getContext) {
        ctx = canvas.getContext('2d');
        ctx.canvas.width = window.innerWidth;
        ctx.canvas.height = window.innerWidth / 2;
        ctx.fillStyle = 'rgb(60,60,60)';
        ctx.fillRect(20, 20, 50, 50);
        ctx.fillRect(80, 20, 50, 50);
        ctx.fillRect(20, 80, 50, 50);
        ctx.fillRect(80, 80, 50, 50);
    }
    
    canvas.addEventListener('click', function(event) {
        var mousePos = getMousePos(canvas, event);
        var x = mousePos.x;
        var y = mousePos.y;
        var pixel = ctx.getImageData(x, y, 1, 1);
        var data = pixel.data;
        var rgba = 'rgb(' + data[0] + ', ' + data[1] + ', ' + data[2] + ')';
        socket.emit('color_pick', {color: rgba})
        console.log('x:' + x + ' y:' + y + ' color:' + rgba);
    }, false);
    
    function getMousePos(canvas, evt) {
        var rect = canvas.getBoundingClientRect();
        return {
            x: evt.clientX - rect.left,
            y: evt.clientY - rect.top
    };
}

    // Callback functions
    socket.on('connect', function() {
        //socket.emit('my_event', {data: 'I\'m connected!'});
    });

    socket.on('init', function(msg) {
        console.log('init ')
        console.log(msg)
        ctx.fillStyle = msg.color1;
        ctx.fillRect(20, 20, 50, 50);
        ctx.fillStyle = msg.color2;
        ctx.fillRect(80, 20, 50, 50);
        ctx.fillStyle = msg.color3;
        ctx.fillRect(20, 80, 50, 50);
        ctx.fillStyle = msg.color4;
        ctx.fillRect(80, 80, 50, 50);
    });
    
    socket.on('put_color', function(msg) {
        console.log('put_color ')
        console.log(msg)
        document.body.style.background = msg.color
    });

    // Handlers for the different forms in the page.
    // These accept data from the user and send it to the server in a
    // variety of ways
    $('form#emit').submit(function(event) {
        socket.emit('my_event', {data: $('#emit_data').val()});
        return false;
    });
    $('form#broadcast').submit(function(event) {
        socket.emit('my_broadcast_event', {data: $('#broadcast_data').val()});
        return false;
    });
    $('form#disconnect').submit(function(event) {
        socket.emit('disconnect_request');
        return false;
    });
    
});
