positions = [
  "Pitcher",
  "Catcher",
  "First Base",
  "Second Base",
  "Shortstop",
  "Third Base",
  "Left Field",
  "Left Center",
  "Right Center",
  "Right Field",
  "Bench",
];

function pickPosition() {
  if (positions.length > 0) {
    var slot = Math.floor(Math.random() * positions.length);
    var pos = positions[slot];
    positions.splice(slot, 1);
  } else {
    var pos = "No more!";
    document.getElementById('posBtn').disabled = true;
  }
  var txt = document.getElementById('posTxt');
  txt.innerHTML = pos;
}
