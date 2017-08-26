function httpGetAsync(theUrl, callback){
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function(){
    if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
      callback(xmlHttp.responseText);
  };
  xmlHttp.open("GET", theUrl, true); // true for asynchronous
  xmlHttp.send(null);
}

var loadSongBtns = document.querySelectorAll('.loadSongBtn');
for (var i = 0; i < loadSongBtns.length; i++) {
  loadSongBtns[i].onclick = function(){
    loadSong(this)
  }
}

function loadSong(btn){
  btn.nextSibling.nextSibling.innerHTML = "<img src='/images/loading.gif' style='width:25px;height:25px;'>";
  httpGetAsync(btn.getAttribute("urltoget"), function(response){
    var parser = new DOMParser();
    var deadTracks = parser.parseFromString(response, "text/html").querySelector("body > div");
    var toReplace = document.getElementById(deadTracks.id);
    toReplace.innerHTML = deadTracks.innerHTML;
    var playlistId = deadTracks.id.split("-")[2];
  });
  btn.remove();
}

var loadAllSongsBtn = document.querySelector('.loadAllSongsBtn');
loadAllSongsBtn.onclick = function(){
  var loadSongBtns = document.querySelectorAll('.loadSongBtn');
  for (var i = 0; i < loadSongBtns.length; i++) {
    loadSong(loadSongBtns[i]);
  }
  this.remove();
};
