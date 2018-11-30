// setting the modal
var modal = document.getElementById('myModal');
var btn = document.getElementById("review-btn");
var span = document.getElementsByClassName("close")[0];

btn.onclick = function() {
    modal.style.display = "block";
}
span.onclick = function() {
    modal.style.display = "none";
}
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
// google maps
function initMap() {
    var lat = parseFloat(latitude);
    var lng = parseFloat(longitude);
    var location = {lat: lat, lng: lng};
    var map = new google.maps.Map(
        document.getElementById('map'), {zoom: 15, center: location}
    );
    var marker = new google.maps.Marker({position: location, map: map});
};