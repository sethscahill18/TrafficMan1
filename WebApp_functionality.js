auth.onAuthStateChanged(user => {
  if (user) {
    console.log('user logged in: ', user);
      setupUI(user);
  } else {
    setupUI(); // this is empty so acts as if not user hence logged out
    console.log('user logged out');
  }
});

const setupUI = (user) => {
  if (user) { // check if user logged in or not
    document.getElementById("logged_in_page").innerHTML = 'Please select between car or light';
    const html = `
      <div>Logged in as ${user.email}</div>
    `;
    accountDetails.innerHTML = html;
    // toggle user UI elements
    loggedInLinks.forEach(item => item.style.display = 'block'); // this makes logged-in links visable
    loggedOutLinks.forEach(item => item.style.display = 'none'); // this makes logged-out links disappear
    // activate/deactive certain buttons
    document.getElementById("Btn_logIn").disabled = true;  // reset the End Trip Button to active
    document.getElementById("Btn_signUp").disabled = true;  // reset the End Trip Button to active
    document.getElementById("Btn_account").disabled = false;  // reset the End Trip Button to active
    document.getElementById("Btn_logOut").disabled = false;  // reset the End Trip Button to active
    document.getElementById("Btn_beCar").disabled = false;  // reset the End Trip Button to active
    document.getElementById("Btn_beLight").disabled = false;  // reset the End Trip Button to active
    document.getElementById("Btn_beginTrip").disabled = true;  // reset the End Trip Button to active
  } else {
    document.getElementById("logged_in_page").innerHTML = 'Please follow the steps below:' +"<br />" + '1. Sign up or Log in.' + "<br />" + '2.Select "Begin Trip"';
    loggedInLinks.innerHTML = '';
    // hide account info
    accountDetails.innerHTML = '';
    // toggle user elements
    loggedInLinks.forEach(item => item.style.display = 'none');
    loggedOutLinks.forEach(item => item.style.display = 'block');
    // activate/deactive certain buttons
    document.getElementById("Btn_logIn").disabled = false;  // reset the End Trip Button to active
    document.getElementById("Btn_signUp").disabled = false;  // reset the End Trip Button to active
    document.getElementById("Btn_account").disabled = true;  // reset the End Trip Button to active
    document.getElementById("Btn_logOut").disabled = true;  // reset the End Trip Button to active
    document.getElementById("Btn_beginTrip").disabled = true;  // reset the End Trip Button to active
    document.getElementById("Btn_beCar").disabled = true;  // reset the End Trip Button to active
    document.getElementById("Btn_beLight").disabled = true;  // reset the End Trip Button to active
  }
};

//Car Selected
const selectedCar = document.getElementById("Btn_beCar");
selectedCar.addEventListener('click', (e) => {
  e.preventDefault();
  // active the Btn_startTrip
  document.getElementById("Btn_beginTrip").disabled = false;  // reset the End Trip Button to active
  document.getElementById("Btn_beLight").disabled = true;  // reset the End Trip Button to active
  document.getElementById("logged_in_page").innerHTML = 'Please click "Begin Trip"!';
});

// create Start Trip
const startTripForm = document.getElementById("Btn_startTrip");
document.getElementById("Btn_endTrip").disabled = true;  // initially have the End Trip button deactivated
startTripForm.addEventListener('click', (e) => {
  e.preventDefault();
  var current_user_email = auth.currentUser.email;
  var userID = auth.currentUser.uid;
  console.log("current_user_email: ", current_user_email );
  navigator.geolocation.getCurrentPosition(function(position){
    firebase.database().ref('cars/' + userID).set({
    user_email: current_user_email,
    active_status: "active",
    vehicle_status: "car",
    time_trip_started: new Date().getTime(),
    coords: {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      time: new Date().getTime()
    }
  }).then(() => {
    // close the create modal & reset form
    const modal = document.querySelector('#modal-create');
    M.Modal.getInstance(modal).close();
    createForm.reset();
  }).catch(err => {
    console.log(err.message);
  });
});
document.getElementById("Btn_endTrip").disabled = false;  // reset the End Trip Button to active
document.getElementById("Btn_startTrip").disabled = true;  // set the Start Trip button to deactive
document.getElementById("Btn_beginTrip").disabled = false;  // set the Start Trip button to deactive
document.getElementById("Btn_logOut").disabled = true;  // set the Start Trip button to deactive
document.getElementById("Btn_account").disabled = true;  // set the Start Trip button to deactive
watchPosition_func(userID);
});

const onclickEndTrip = document.getElementById("Btn_endTrip");
onclickEndTrip.addEventListener('click', (e) => {
  e.preventDefault();
  // stop the setInteval , end timeput inteval here
  // clearInterval(controlInterval_id);
  // end watchPosition tracking
  navigator.geolocation.clearWatch(id_of_trip);
  // and set active_status to inactive
  var current_user_email = auth.currentUser.email;
  var userID = auth.currentUser.uid;
  // db.collection('cars').doc(current_user_email).update({
  firebase.database().ref('cars/' + userID).update({
    active_status: "inactive"
  });
  console.log("trip ended: ", current_user_email)
  document.getElementById("Btn_startTrip").disabled = false;  // reset the Start Trip button to active
  document.getElementById("Btn_endTrip").disabled = true;  // reset the End Trip Button to deactive
  document.getElementById("Btn_beginTrip").disabled = false;  // set the Start Trip button to deactive
  document.getElementById("Btn_logOut").disabled = false;  // set the Start Trip button to deactive
  document.getElementById("Btn_account").disabled = false;  // set the Start Trip button to deactive
});

var id_of_trip
function watchPosition_func(userID){
  id_of_trip = navigator.geolocation.watchPosition(function(position_from_watch){
      firebase.database().ref('cars/' + userID).update({
      coords:{
        latitude: position_from_watch.coords.latitude,
        longitude: position_from_watch.coords.longitude,
        time: new Date().getTime()
      }
    });

},function(error){
  console.log("error msg");
  document.getElementById("Btn_startTrip").disabled = false;  // reset the Start Trip button to active
  clearTimeout(location_timeout);
  geolocFail();
}, {maximumAge:7000,timeout: 10000, enableHighAccuracy: false}); // was changed to 30000 but results weren't great
console.log("id_of_trip: " + id_of_trip)
}

function newSample(userID){
  navigator.geolocation.getCurrentPosition(function(position){
      // db.collection('cars').doc(current_user_email).update({
      firebase.database().ref('cars/' + userID).update({
      coords:{
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        time: new Date().getTime()
      },
    });
});
};

// sign up
const signupForm = document.querySelector('#signup-form');
signupForm.addEventListener('submit', (e) => {
  e.preventDefault();

  // get user info
  const email = signupForm['signup-email'].value;
  const password = signupForm['signup-password'].value;

  // sign up the user
  auth.createUserWithEmailAndPassword(email, password).then(cred => {
    // close the signup modal & reset form
    const modal = document.querySelector('#modal-signup');
    M.Modal.getInstance(modal).close();
    signupForm.reset();
  });
});


const onclickLogIn = document.getElementById("Btn_logIn");
onclickLogIn.addEventListener('click', (e) => {
  e.preventDefault();
  const modal = document.querySelector('#modal-login');
  M.Modal.getInstance(modal).open();
});

const onclickBeginTrip = document.getElementById("Btn_beginTrip");
onclickBeginTrip.addEventListener('click', (e) => {
  e.preventDefault();
  const modal = document.querySelector('#modal-startTrip');
  M.Modal.getInstance(modal).open();
});

const onclickBeLight = document.getElementById("Btn_beLight");
onclickBeLight.addEventListener('click', (e) => {
  e.preventDefault();
  const modal = document.querySelector('#modal-lightSelection');
  M.Modal.getInstance(modal).open();
});

// light selection form
const selectLightForm = document.querySelector('#selectLight-form');
selectLightForm.addEventListener('submit', (e) => {
  e.preventDefault();
  // lane Selected from the firbase list of lanes
  const laneSelected = selectLightForm['lane_number'].value;
  var current_user_email = auth.currentUser.email;
  firebase.database().ref('lanes/' + laneSelected).update({
    userId: current_user_email
  });
  // retrive data from firebase
  firebase.database().ref('lanes/' + laneSelected + '/light_colour/').on('value', gotData_lightColour, errData);
  // document.getElementById("logged_in_page").innerHTML = 'Lane Selected: ' + laneSelected;
  const modal = document.querySelector('#modal-lightSelection');
  M.Modal.getInstance(modal).close();
  selectLightForm.reset();//
  // ask firebase for information regarding lane_selected
  // opem a modal that displays the lane selected and GO and STOP buttons
  const modal_2 = document.querySelector('#modal-laneControlDisplay');
  // modal_2.find('.modal-title').text('HELLO');
  document.getElementById("Btn_displayGO").disabled = true;
  document.getElementById("Btn_displaySTOP").disabled = true;
  document.getElementById("laneControlDisplayHeader").innerHTML = 'Traffic Light Control For Lane: ' + laneSelected;
  M.Modal.getInstance(modal_2).open();
});

function gotData_lightColour(data){
  var light_colour = data.val();
  controlLights (light_colour) // may not need laneSelected
}

function errData(err){
  console.log('Error!');
  console.log(err);
}

function controlLights (light_colour){
  if (light_colour == 'red'){
    document.getElementById("Btn_displayGO").disabled = true;
    document.getElementById("Btn_displaySTOP").disabled = false;
  }
  if (light_colour == 'green'){
    document.getElementById("Btn_displayGO").disabled = false;
    document.getElementById("Btn_displaySTOP").disabled = true;
  }
  if (light_colour != 'green' && light_colour != 'red'){
    document.getElementById("Btn_displayGO").disabled = true;
    document.getElementById("Btn_displaySTOP").disabled = true;
  }
}

const onclickSignUp = document.getElementById("Btn_signUp");
onclickSignUp.addEventListener('click', (e) => {
  e.preventDefault();
  const modal = document.querySelector('#modal-signup');
  M.Modal.getInstance(modal).open();
});

const onclickAccount = document.getElementById("Btn_account");
onclickAccount.addEventListener('click', (e) => {
  e.preventDefault();
  const modal = document.querySelector('#modal-account');
  M.Modal.getInstance(modal).open();
});

// logout
const logout = document.getElementById("Btn_logOut");
logout.addEventListener('click', (e) => {
  e.preventDefault();
  auth.signOut();
});

//  login
const loginForm = document.querySelector('#login-form');
loginForm.addEventListener('submit', (e) => {
 e.preventDefault();

 // get user info
 const email = loginForm['login-email'].value;
 const password = loginForm['login-password'].value;

 // log the user in
 auth.signInWithEmailAndPassword(email, password).then((cred) => {
   // close the login modal & reset form
   const modal = document.querySelector('#modal-login');
   M.Modal.getInstance(modal).close();
   loginForm.reset();
 });
});
