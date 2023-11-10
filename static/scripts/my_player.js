var SESSION_STATUS = Flashphoner.constants.SESSION_STATUS;
var STREAM_STATUS = Flashphoner.constants.STREAM_STATUS;
var session;

function init_api() {
    console.log("init api");
         Flashphoner.init({
});
}

function connect() {
    session = Flashphoner.createSession({urlServer: "wss://demo.flashphoner.com"}).on(SESSION_STATUS.ESTABLISHED, function(session){    
console.log("connection established");
playStream(session);
});
}