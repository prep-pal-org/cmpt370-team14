//for the timer function

// Track all intervals + remaining time
let timers = {};

function startTimer(seconds, stepId) {
    clearInterval(timers[stepId]?.interval);

    timers[stepId] = {
        remaining: seconds,
        interval: null,
        isPaused: false
    };

    // Button visibility
    document.getElementById(`start-${stepId}`).style.display = "none";
    document.getElementById(`pause-${stepId}`).style.display = "inline-block";
    document.getElementById(`resume-${stepId}`).style.display = "none";

    timers[stepId].interval = setInterval(() => {
        if (!timers[stepId].isPaused) {
            updateTimerDisplay(stepId);

            timers[stepId].remaining--;

            if (timers[stepId].remaining < 0) {
                clearInterval(timers[stepId].interval);
                alert("Step finished!");
            }
        }
    }, 1000);

    updateTimerDisplay(stepId);
}

function pauseTimer(stepId) {
    timers[stepId].isPaused = true;

    document.getElementById(`pause-${stepId}`).style.display = "none";
    document.getElementById(`resume-${stepId}`).style.display = "inline-block";
}

function resumeTimer(stepId) {
    timers[stepId].isPaused = false;

    document.getElementById(`pause-${stepId}`).style.display = "inline-block";
    document.getElementById(`resume-${stepId}`).style.display = "none";
}

function updateTimerDisplay(stepId) {
    const display = document.getElementById(`display-${stepId}`);

    let sec = timers[stepId].remaining;
    let m = Math.floor(sec / 60);
    let s = sec % 60;

    display.innerText = `${m}:${s.toString().padStart(2, "0")}`;
}
