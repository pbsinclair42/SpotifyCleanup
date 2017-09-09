var BASE_URL = "http://localhost:5000/";
var lastHttpRequest;

function httpGetAsync(theUrl, callback){
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function(){
    if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
      callback(xmlHttp.responseText);
  };
  xmlHttp.open("GET", theUrl, true); // true for asynchronous
  xmlHttp.send(null);
  return xmlHttp
}

function createTrack(context){
  var source = $("#trackTemplate").html();
  var template = Handlebars.compile(source);
  try {
    context['added_at'] = context['added_at'].split('T')[0];
  } catch (TypeError) {
    context['added_at'] = "Unknown"
  }
  if (!context['albumArt']) {
    context['albumArt'] = "http://i1156.photobucket.com/albums/p580/keca-pooh22/albumart_mp_unknown.png"
  }
  context['artists'] = context['artists'].join(', ');
  return template(context).trim();
}

function createTrackRow(tracks){
  var trackRow = '<div class="trackRow">';
  tracks.forEach(function(track, i){
    trackRow += createTrack(track)
  });
  trackRow += "</div>";
  return trackRow;
}

function createLoadingGif(id){
  var source = $("#loadingGifTemplate").html();
  var template = Handlebars.compile(source);
  var context = {
    id:id || ""
  };
  return template(context).trim();
}

function makeSelectable(selector, onNewClick){
  $(selector).click(function(){
    if ($(this).hasClass("selected")) {
      return;
    }
    $(selector + '.selected').removeClass("selected");
    $(this).addClass("selected");
    onNewClick(this);
  });
}

function loadDuplicates(currentPlaylist){
  if (lastHttpRequest !== undefined) {
    console.log(lastHttpRequest);
    lastHttpRequest.abort();
  }
  var tracksDisplay = $('.tracksDisplay');
  tracksDisplay.empty();
  $(createLoadingGif('playlistLoading')).appendTo(tracksDisplay);
  url = BASE_URL + "duplicates/?playlistId=" + currentPlaylist.id + "&playlistName=" + currentPlaylist.innerHTML + "&owner=" + currentPlaylist.owner;
  lastHttpRequest = httpGetAsync(url, function(data){
    $('.tracksDisplay').empty();
    $('#playlistLoading').remove();
    data = JSON.parse(data);
    console.log(data);
    if (data.length === 0) {
      $("<div class='emptyTracksInfoBox'>No duplicates found!</div>").appendTo(tracksDisplay);
    } else {
      data.forEach(function(tracks, i){
        $(createTrackRow(tracks)).appendTo(tracksDisplay);
      });
    }
  });
}

function loadDeads(currentPlaylist){
  if (lastHttpRequest !== undefined) {
    console.log(lastHttpRequest);
    lastHttpRequest.abort();
  }
  var tracksDisplay = $('.tracksDisplay');
  tracksDisplay.empty();
  $(createLoadingGif('playlistLoading')).appendTo(tracksDisplay);
  url = BASE_URL + "deads/?playlistId=" + currentPlaylist.id + "&playlistName=" + currentPlaylist.innerHTML + "&owner=" + currentPlaylist.owner;
  lastHttpRequest = httpGetAsync(url, function(data){
    $('.tracksDisplay').empty();
    $('#playlistLoading').remove();
    data = JSON.parse(data);
    console.log(data);
    if (data.length === 0) {
      $("<div class='emptyTracksInfoBox'>No dead tracks found!</div>").appendTo(tracksDisplay);
    } else {
      data.forEach(function(tracks, i){
        $(createTrackRow([tracks])).appendTo(tracksDisplay);
      });
    }
  });
}

function loadDuplicatesOrDeads(){
  try {
    currentPlaylistTab = $('.playlistItem.selected')[0];
    currentPlaylist = {
      'id':currentPlaylistTab.id,
      'name':currentPlaylistTab.innerHTML,
      'owner':currentPlaylistTab.getAttribute("owner")
    };
  } catch (TypeError) {
    // no playlist yet selected
    return;
  }
  currentTab = $('.tab.selected')[0].id;
  switch (currentTab) {
    case "duplicates":
      loadDuplicates(currentPlaylist);
      break;
    case "deads":
      loadDeads(currentPlaylist);
      break;
    default:
      console.error("Unknown tab type: " + currentTab);
  }
}

$(function(){

  makeSelectable(".playlistItem", loadDuplicatesOrDeads);

  makeSelectable(".tab", loadDuplicatesOrDeads);

  $('#duplicates').click();
});
