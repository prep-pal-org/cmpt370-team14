//for the timer function

function startTimer(seconds, displayId) {
    let timeLeft = seconds;

    const interval = setInterval(() => {
        const minutes = Math.floor(timeLeft / 60);
        const sec = timeLeft % 60;

        document.getElementById(displayId).innerText =
            `${minutes}:${sec.toString().padStart(2,'0')}`;

        timeLeft--;

        if (timeLeft < 0) {
            clearInterval(interval);
            alert("Step finished!");
        }
    }, 1000);
}

