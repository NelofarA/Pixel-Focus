// https://www.youtube.com/watch?v=PIiMSMz7KzM&t=13s 
//https://www.youtube.com/watch?v=37oiMs3-J_s
// timer video used for reference

// used the two below to find all visiblity, mouse and window movement events 
// to trigger hazardLevel (to prevent cheating in the timer)
//https://www.w3schools.com/jsref/obj_mouseevent.asp
//https://developer.mozilla.org/en-US/docs/Web/API/UI_Events

//setTimeout tutorial
//https://www.youtube.com/watch?v=shWr5DNVeCI

//audio 
//https://www.youtube.com/watch?v=3xlws5og44U
//https://www.youtube.com/watch?v=Kcvg0jXwrvU (around 8 min into the video)
//https://www.youtube.com/watch?v=K6Qm10njblQ
//https://stackoverflow.com/questions/55490155/how-to-autoplay-audio-when-the-countdown-timer-is-finished
//https://pixabay.com/sound-effects/musical-lo-fi-alarm-clock-243766/ audio file credit for timer alarm
//https://pixabay.com/sound-effects/musical-hurt-c-08-102842/ audio file credit for damage taken sound
//https://pixabay.com/sound-effects/film-special-effects-failure-1-89170/ audio file credit for failure sound

// (not taught in class, needed a way how to send info/variable from Javasript to Flask)
// for fetch API 
//https://www.youtube.com/watch?v=5VCY9yCZnlc 
//https://www.youtube.com/watch?v=6AfiFfiBUME
//https://www.youtube.com/watch?v=QKcVjdLEX_s
//https://www.youtube.com/watch?v=QKcVjdLEX_s <--- Heavily referenced for fetch use 
// Note: If I forgort to credit something on the project write up all the credits/reference are here

// js + css animation 
//https://www.youtube.com/watch?v=LE9EaIZdjFM&t=9s

const alarmSound = new Audio("../static/alarm_Sound.mp3");
const alarmSound2 = new Audio("../static/alarm_Sound.mp3");
// aparently stacking audio make it louder
const damageSound = new Audio("../static/damage_Sound.mp3");
const failureSound = new Audio("../static/failure_Sound.mp3");
alarmSound.volume = 1;
alarmSound2.volume = 1;
damageSound.volume = 0.5;
failureSound.volume = 0.5;


let isPaused = false; //Start as paused unitl the user clicks start
let isFocusing = false;
let timerInterval;
let timeleft;
let initialTime;
let cooldownInterval;
let cooldownTime = 5;
let cooldownTimeout; 
let hazardImmunity = false;
let hazardLevel = 0;
let goodEnding = true; 
let isGameOver = false; 


const timerDisplay = document.getElementById("timer");
const startBtn = document.getElementById("start_timer");
const timerDurationInput = document.getElementById("timer_duration");

const hazardFill = document.getElementById("hazard_fill");
const hazardWater = document.getElementById("hazard_img");
const gameImage = document.getElementById("game_image");
const statusFocus = document.getElementById("status_focus");
const progressPercent = document.getElementById("progress_precent");
const progressBar = document.getElementById("progress_bar");

const endSceneOverlay = document.getElementById("ending_popup");
const endingTitle = document.getElementById("ending_title");
const endingMessage = document.getElementById("ending_message");
const endingImage = document.getElementById("ending_image");
const closeOverlayBtn = document.getElementById("closeOverlayButton");

let selectedSkillID = "";
// the get Id was here but it has to update every time before timer starts

// ------------------------ Event Listeners ----------------------
startBtn.addEventListener("click", startTimer);

document.addEventListener("keydown", (event) => {
    if (event.code === "Space") {
     event.preventDefault(); 
        // searched it up cause there was a delay on the pausing timer event
        // It wouldn't pause unless you hold it a couple more seconds instead of
        // instantly pausing, apparently it is caused by the space doing a "scroll down action"
        togglePause();
    } else if (event.code === "KeyR") {
        resetTimer();
    }
    }); 

// need to add event listener for movemouse and mouse off tab or something
// maybe use onmouseout or mouseleave and visibitychange for that
document.addEventListener("mousemove", updateHazard);
document.addEventListener("mouseout", updateHazard);
document.addEventListener("mouseleave", updateHazard);
document.addEventListener("visibilitychange", updateHazard);
window.addEventListener('blur', updateHazard); 
window.addEventListener('focus', updateHazard); 

/**NOTEE: choose not to enable window visiblity/change as a user could be working on
a different window and just wants to have the timer open on the side while they work
(maybe in the future/for fun I can add a block website list that the user can fill)
**/
closeOverlayBtn.addEventListener("click", closeOverlay);


/**new to js so here is some reminder 
- console.log() is used to print something
- addEventListener("event", function) is used to listen for an event on an element 
- setInterval(function, time) is used to call a function repeatedly
- end every statement with ; and use {} to group statements/function
-  for js if condition must be in () and ! before a variable is the not equvalent of python
    also make sure if block is in {}
- (===) in js is the equvalent of (==) in python but also checks for type so it is better to use than (==) in js 
-  logic opperator and is (&&) in js and or is (||) in js
-  for loop in js is for (let i = 0; i < 10; i++) or for (let item of items) eqvalent of for item in list in python
-  elif is else if in is 
- `${name}` is the equvalent of f"{name}" in python
- timeDuration-- is the equvalent of timeDuration -= 1 or timeDuration = timeDuration - 1 in python
    it is a decrement opperator
- => this is NOT INEQUALITY in js it is used for arrow functions like const func = () => {} and it is a shorter way to write function expressions
- ? is "ternary operator" short way of wrtingin if else statement like condition ? exprIfTrue : exprIfFalse its confusing so might not use
**/ 


// ------------------------ Timer Functions ----------------------


function startTimer() {
    //maybe request full screen?
    alarmSound.play();
    alarmSound2.play();
    alarmSound.pause();
    alarmSound2.pause();
    alarmSound.currentTime = 0;
    alarmSound2.currentTime = 0;
    // need to do it up here cause it has to be user activate or else
    // does work without it but just in case it doesn't let me play it later 

    clearInterval(timerInterval);
    clearInterval(cooldownInterval);

    selectedSkillID = document.getElementById('skill_select').value;

    if (!selectedSkillID) {
        alert("Please select a skill to use the timer, If have not added a skill please go to the flaskcard section to add one. ");
        return;

    } 
    if (isFocusing && !isPaused) return;
    // if the timer is not paused/already running return so it doesnt start another timer
    
    if (!isFocusing && !isPaused){
        // if !isPaused => if not isPaused and isPaused starts at false so if not false = true 
        // if isPaused = True then !isPaused is false and startTimer does nothing
        if (timerDurationInput.value < 1){
            timerDurationInput.value = 1;
            alert("Timer must be at least 10 mins");
            //NOTE MIN VALUE IS CURRENT 1 ON PURPOSE SO YOU DON'T HAVE TO WAIT TEN MINUTES TO CHECK 
            // IF IT WORKS OR IF THE GAIN XP
            return;
        }
        timeleft = timerDurationInput.value * 60;
        initialTime = Number(timerDurationInput.value);
        // need this cause the total time of the session is set to database 
        // if completed and timeleft is for the actual timer which decrease from the total
    }// in seconds

    isPaused = false;
    isFocusing = true;
    statusFocus.textContent = "Focusing...";
    cooldown(); //initial 5 sec grace period
    
    clearInterval(timerInterval);
    // if there is already a timer running clear it before starting a new one
    timerInterval = setInterval(() => {
        if (timeleft <= 0) {
            clearInterval(timerInterval);
    


            //TODO: ADD ALARM SOUND STUFF HERE
            isFocusing = false ;
            isPaused = false;
            isGameOver = false; 
            statusFocus.textContent = "Completed Session";
            alarmSound.play();
            alarmSound2.play();

              setTimeout(() => {
                alarmSound.pause();
                alarmSound2.pause();
                alarmSound.currentTime = 0;
                alarmSound2.currentTime = 0;
                // rewinds/reset audio for next play 
            },10000);
            // plays for 10 seconds then seTimeout pauses it after a 10 second delay
            
            endSession(); 
            sendStatsToFlask();
            // CALLS FUNCTION THAT SENDS THE TIME OF COMPLETED SESSION ONLY 
            //this info is used to be displayed on my progress section
            
            
          
    


        } else { 
            if (document.visibilityState === 'hidden' || !document.hasFocus()
            ) {
                updateHazard(); 
                // found a issue where if you move off tab during immunity
                // it did not update Hazard level catches if ppl hide on a different
                // tab to prevent infraction checks 
                // here because it checks it every sec in timer function
            }

                timeleft--;
                // -- is equvalent of python =-1
                let minutes = Math.floor(timeleft / 60);
                // Math.floor() is equivalent of // (integer division) python  rounds down to the nearest int
                let seconds = timeleft % 60;

                let secondsDisplay = seconds;
                if (seconds < 10) {
                    secondsDisplay = "0" + seconds;
                }

        timerDisplay.textContent = `${minutes}:${secondsDisplay}`;
            }
    }, 1000); //apparently need 1000 cause 1000milisec is 1 second so the timer counts down every second
    // aka runs the whole block every second (why setInterval is used over a loop)
}

//-------------------------- PAUSE FUNCTION -----------------------------------------

function togglePause() {
   console.log("toggling pause");
  
   if (isFocusing === true) {
        clearInterval(timerInterval);
        clearInterval(cooldownInterval);
        isPaused = true;
        isFocusing = false;
        statusFocus.textContent = "Paused";
        return;
        }
        // save last paused time in a variable 

    else {
        startTimer();
        // figure out to start the timer from the last pause save
        return;
        }
   
} 

// --------------------------RESET TIMER -------------------------------------
   
 function resetTimer(){
    clearInterval(timerInterval);
    clearInterval(cooldownInterval); 
    hazardImmunity = false;
    goodEnding = true;
    //hazardfill = false; Once hazard filll is implimented 
    isPaused = false; 
    isFocusing = false;
    let minutes = timerDurationInput.value || 25;  // either input value or default
    timeleft = minutes * 60; 
    statusFocus.textContent = "Start Focusing?"; 
    startBtn.textContent = "Start"; 
    timerDisplay.textContent = `${minutes}:00`;
    
    hazardLevel = 0;
    progressBar.value = 0;
    progressPercent.textContent = "Hazard level 0%";
    endingImage.src = "";
    endingMessage = "";
    endingTitle = ""; 
    isGameOver = false;
    gameImage.src = "../static/game_scene.png";
    hazardWater.style.transform = `translateY(20%)`;
    return; 
    
}
//---------------------------Game Logic ----------------------
function updateHazard() {
    /**
     Function updates hazard level both on danger level progress bar and 
    and visually on the game screen raising lava/water/etc height
     **/
    if (!isFocusing || isPaused || hazardImmunity || hazardLevel >= 100) return; 

    console.log("updating hazard");
    if (hazardLevel === 0){
        hazardLevel = 33;
        progressPercent.textContent = "Hazard Level 33%";
        progressBar.value = 33;
        gameImage.src = "../static/game_scene2.png";

        hazardWater.animate([ 
        {
        transform: "translateY(100%)",
        },
        {transform: "translateY(80%)",
        }],
        {
            duration: 2000,
        }
        );
        hazardWater.style.transform = `translateY(80%)`;
        // animation goes away so i have to set it still for the next part


        // temporarily disable/remove mouse event listeners and call the 
        //cooldown function that counts 5-10 sec and re-enable EventListener
        cooldown();
        damageSound.play(); 
            setTimeout(() => {
                damageSound.pause();
                damageSound.currentTime = 0; 
            },1000);

        // spmething update hazardFill to change css to a higher lava ammount
    }

    else if (hazardLevel === 33){
        hazardLevel = 66;
        progressPercent.textContent = "Hazard Level 66%";
        progressBar.value = 66;
        gameImage.src = "../static/game_scene3.png";
        hazardWater.animate([ 
        {
        transform: "translateY(80%)",
        },
        {transform: "translateY(60%)",
        }],
        {
            duration: 1500,
        }
        );
        hazardWater.style.transform = `translateY(60%)`;

        cooldown();
        // spmething update hazardFill to change css to a higher lava ammount
        damageSound.play(); 
        setTimeout(() => {
            damageSound.pause();
            damageSound.currentTime = 0;
        },1000);
    }
    else if (hazardLevel === 66) {
        hazardLevel = 99;
        progressPercent.textContent = "Hazard Level 99%";
        progressBar.value = 99;
        gameImage.src = "../static/game_scene4.png";
        hazardWater.animate([ 
        {
        transform: "translateY(60%)",
        },
        {transform: "translateY(40%)",
        }],
        {
            duration: 1500,
        }
        );
        hazardWater.style.transform = `translateY(40%)`;

        cooldown();
        // spmething update hazardFill to change css to a higher lava ammoun
         damageSound.play(); 
            setTimeout(() => {
                damageSound.pause();
                damageSound.currentTime = 0; 
            },1000);
    }

    else if (hazardLevel === 99){
        hazardLevel = 100;
        progressPercent.textContent = "Hazard Level 100%";
        progressBar.value = 100;
        goodEnding = false;
        gameImage.src = "../static/game_scene5.png";
        hazardWater.animate([ 
        {
        transform: "translateY(40%)",
        },
        {transform: "translateY(5%)",
        }],
        {
            duration: 1000,
        }
        );
        hazardWater.style.transform = `translateY(5%)`;

        failureSound.play(); 
            setTimeout(() => {
                failureSound.pause();
                failureSound.currentTime = 0; 
            },3000);

        //resetTimer();

        clearInterval(timerInterval);
        statusFocus.textContent = "Focus was broken"

        // cant clear hazard bar here or clear it once the popup after the ending 
        // says contiune Focusing
         setTimeout(() => {
                endSession();
            },2000);
        //delay for calling endsession
        // spmething update hazardFill to change css to a higher lava ammount

    }
    
    
}

// --------------------- COOLDOWN FUNCTION ----------------------------------

function cooldown(){ // in seconds
    hazardImmunity = true;
    if (cooldownTime <=0) {
        cooldownTime = 5;
    }

    statusFocus.textContent = `Hazard Immunity Cooldown ${cooldownTime} seconds`;
    clearInterval(cooldownInterval);
    clearTimeout(cooldownTimeout);
    // found a bug where it reset immunity to 5 after pausing so it gives inf imunity

    /** done the same way the timer was done cause I learnt that doing it like
    setTimeout(function,delay) runs it instantly) instead doing it like this tells
    it to wait 5s and then do what is inside, also lets you do a list of commands inside the {}
    **/
    cooldownTimeout = setTimeout(() => {
            if (isFocusing && !isPaused){
                hazardImmunity = false;
                statusFocus.textContent = "Focusing...";
                cooldownTime = 0;
            }
        }, cooldownTime * 1000);
        // better to do it cooldownTime * 1000 then cooldown = 5000 cause tracks what
        // time you leave off on the cooldown after you un-pause (prevents infinit cooldown glitch)


    cooldownInterval = setInterval(() => {
        cooldownTime--;
        if (cooldownTime <= 0){
            clearInterval(cooldownInterval);
        } else { 
            statusFocus.textContent = `Hazard Immunity Cooldown ${cooldownTime} seconds`;
        }
        }, 1000); 
        
    return;
}

    // sereach and found out that setTimeout does that, was about to do it manually


// ------------------------------END GAME FUNCTION---------------------
function endSession() {
    console.log("ending session");


    if (isGameOver) return;

    isGameOver = true;
    // locks it in

    isFocusing = false;
    //stops game 
   
    clearInterval(timerInterval);
    clearInterval(cooldownInterval)
    

    if (goodEnding === false){
        endingTitle.textContent = "You Lost Focus";
        endingMessage.textContent = "A new victim has perished. Do better next time...";
        endingImage.src = "../static/Bad_ending.png";
        endSceneOverlay.style.display = "flex";
        //ending screen with bad ending image 
    }

    if (goodEnding === true) {
        // need the happy animal overlay 
        endingTitle.textContent = "A succesful session has been completed!"
        endingMessage.textContent = "Congrats on staying focused! You earned XP!"
        endingImage.src = "../static/good_ending.png";
        endSceneOverlay.style.display = "flex"; 
        // ending_text
    }

    else return;
    // if failed link bad ending popuo if success link good ending popup
    // checks the condition of the focus session/if timer ended due to failure/or hp reaching 0 
    // idk which one will be the easiest condition to check yet
}

// -----------------------CLOSE POPUP ------------------------------------

function closeOverlay(){
    // insert close overlay here or make display = none (CSS)
    endSceneOverlay.style.display = 'none';
    endSceneOverlay.style.display = 'none';
    isGameOver = false;
    gameImage.src = "../static/game_scene.png";
    hazardWater.style.transform = `translateY(100%)`;
    resetTimer();
    
    if (alarmSound) {
        alarmSound.pause();
        alarmSound.currentTime = 0;
    }
    if (alarmSound2) {
        alarmSound2.pause();
        alarmSound2.currentTime = 0;
    }
}

// ------------------------ SEND STATS -------------------------------
// neeed to use fetch so the page doesnt reset as the stats are being saved

function sendStatsToFlask() {

    const dataCollected = {
        skill_id: selectedSkillID,
        time: initialTime,
    };

     fetch('http://127.0.0.1:5000/saveTimerStats', {
        method: 'POST',
        credentials: "include",
        body: JSON.stringify(dataCollected),
        cache: "no-cache",
        headers: new Headers({ "content-type": "application/json"})
    });



}

