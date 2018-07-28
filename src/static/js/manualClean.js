var BASE_URL = "http://localhost:5000/";
var lastHttpRequest;
var playlistCache = {};

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

function createTrackRow(tracks){
  var trackRow = '<div class="trackRow">';
  tracks.forEach(function(track, i){
    trackRow += createTrack(track)
  });
  trackRow += "</div>";
  return trackRow;
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

function loadDuplicates(data){
  var tracksDisplay = $('.tracksDisplay');
  tracksDisplay.empty();
  var duplicateTracks = data['duplicateTracks'];
  if (duplicateTracks.length === 0) {
    $("<div class='emptyTracksInfoBox'>No duplicates found!</div>").appendTo(tracksDisplay);
  } else {
    duplicateTracks.forEach(function(tracks, i){
      $(createTrackRow(tracks)).appendTo(tracksDisplay);
    });
  }
}

function loadDeads(data){
  var tracksDisplay = $('.tracksDisplay');
  tracksDisplay.empty();
  var unplayableTracks = data['unplayableTracks'];
  if (unplayableTracks.length === 0) {
    $("<div class='emptyTracksInfoBox'>No dead tracks found!</div>").appendTo(tracksDisplay);
  } else {
    unplayableTracks.forEach(function(tracks, i){
      $(createTrackRow([tracks])).appendTo(tracksDisplay);
    });
  }
}

function load(currentPlaylist, callback){
  if (lastHttpRequest !== undefined) {
    lastHttpRequest.abort();
  }
  var tracksDisplay = $('.tracksDisplay');
  tracksDisplay.empty();
  $(createLoadingGif('playlistLoading')).appendTo(tracksDisplay);
  if (playlistCache[currentPlaylist.id] !== undefined) {
    callback(playlistCache[currentPlaylist.id]);
  } else {
    var url = BASE_URL + "getCleanupData/?playlistId=" + currentPlaylist.id + "&playlistName=" + currentPlaylist.name +
      "&owner=" + currentPlaylist.owner + "&snapshot_id=" + currentPlaylist.snapshot_id;
    lastHttpRequest = httpGetAsync(url, function(data){
      data = JSON.parse(data);
      playlistCache[currentPlaylist.id] = data;
      callback(data);
    });
  }
}

function loadDuplicatesOrDeads(){
  try {
    var currentPlaylistTab = $('.playlistItem.selected')[0];
    var currentPlaylist = {
      'id': currentPlaylistTab.id,
      'name': currentPlaylistTab.innerHTML,
      'owner': currentPlaylistTab.getAttribute("owner"),
      'snapshot_id': currentPlaylistTab.getAttribute("snapshot_id")
    };
  } catch (TypeError) {
    // no playlist yet selected
    return;
  }
  var currentTab = $('.tab.selected')[0].id;
  switch (currentTab) {
    case "duplicates":
      load(currentPlaylist, loadDuplicates);
      break;
    case "deads":
      load(currentPlaylist, loadDeads);
      break;
    default:
      console.error("Unknown tab type: " + currentTab);
  }
}

$(function(){
  $(createVolumeControl("globalVolumeControl", 10, 'body')).appendTo($('.volumeContainer'));

  makeSelectable(".playlistItem", loadDuplicatesOrDeads);

  makeSelectable(".tab", loadDuplicatesOrDeads);

  $('#duplicates').click();
});
