function createTrack(title, artists, duration, added_at, album, albumArt, trackId, index){
  var source = document.querySelector("#trackTemplate").innerHTML;
  var template = Handlebars.compile(source);
  var context = {
    title:title,
    artists:artists,
    duration:duration,
    added_at:added_at,
    album:album,
    albumArt:albumArt,
    trackId:trackId,
    index:index
  };
  return template(context).trim();
}

$(createTrack("1+1", "Scouting For Girls", "2:48", "2017-12-02", "Everybody Wants To Be On TV", "https://i.scdn.co/image/f00ff9ba4dcd76b344b8fd3fbccd4d507437dcc6", "asdf", 0)).appendTo($('.trackRow'));
$(createTrack("1+1", "Scouting For Girls", "2:48", "2017-12-02", "Everybody Wants To Be On TV", "https://i.scdn.co/image/f00ff9ba4dcd76b344b8fd3fbccd4d507437dcc6", "asdf", 1)).appendTo($('.trackRow'));