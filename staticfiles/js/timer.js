document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // SETTINGS (SAFE LOAD)
    // =========================
    const soundEl = document.getElementById("sound-enabled");
    const soundEnabled = soundEl ? JSON.parse(soundEl.textContent) : false;

    //const focusDuration = Number(focusDuration);
    //const breakDuration = Number(breakDuration);
    //const totalCycles = Number(totalCycles);

    // =========================
    // SOUNDS
    // =========================
    const focusStartSound = new Audio("/static/audio/focus_start.mp3");
    const breakStartSound = new Audio("/static/audio/break_start.mp3");
    const endSound = new Audio("/static/audio/end.mp3");

    const timerDisplay = document.getElementById("timer");
    const modeLabel = document.getElementById("modeLabel");
    const statsBox = document.getElementById("focus-stats");

    if (!timerDisplay) return;

    // =========================
    // STATE
    // =========================
    let timer = null;
    let isRunning = false;
    let isBreak = false;
    let cycleCount = 0;
    let firstStart = true;

    let time = focusDuration * 60;

    // =========================
    // DISPLAY TIME
    // =========================
    function displayTime() {
        let mins = Math.floor(time / 60);
        let secs = time % 60;

        timerDisplay.innerText =
            `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // =========================
    // UPDATE TIMER
    // =========================
    function updateTimer() {
        if (time <= 0) {
            pauseTimer();
            switchMode();
            return;
        }

        time--;
        displayTime();
    }

    // =========================
    // START TIMER
    // =========================
    function startTimer() {
        if (isRunning) return;

        if (firstStart) {
            firstStart = false;
            isBreak = false;
            time = focusDuration * 60;

            if (soundEnabled) {
                focusStartSound.play().catch(() => {});
            }

            if (modeLabel) {
                modeLabel.innerText = "Focus Time 🎯";
            }
        }

        isRunning = true;
        timer = setInterval(updateTimer, 1000);
    }

    // =========================
    // PAUSE TIMER
    // =========================
    function pauseTimer() {
        isRunning = false;
        clearInterval(timer);
        timer = null;
    }

    // =========================
    // RESET TIMER
    // =========================
    function resetTimer() {
        pauseTimer();

        isBreak = false;
        cycleCount = 0;
        firstStart = true;

        time = focusDuration * 60;
        displayTime();

        if (modeLabel) {
            modeLabel.innerText = "Focus Time 🎯";
        }
    }

    // =========================
    // SAVE SESSION
    // =========================
    function saveSession() {

        fetch("/base/save-focus-session/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                duration: focusDuration
            })
        })
        .then(res => res.json())
        .then(data => {
            console.log("Saved:", data);
            const todayFocus = document.getElementById("todayFocus");
            if (todayFocus) {
                todayFocus.textContent =
                    parseInt(todayFocus.textContent) + focusDuration;
            }
            if (statsBox) {
                statsBox.classList.add("updated");
                setTimeout(() => {statsBox.classList.remove("updated");}, 500);
            }
        })
        .catch(err => console.log("Save error:", err));
    }

    // =========================
    // SWITCH MODE
    // =========================
    function switchMode() {

        if (!isBreak) {

            saveSession();
            cycleCount++;

            if (cycleCount >= totalCycles) {

                if (soundEnabled) {
                    endSound.play();
                }

                alert("All cycles completed!");
                pauseTimer();
                return;
            }

            isBreak = true;
            time = breakDuration * 60;

            if (soundEnabled) {
                breakStartSound.play();
            }

            if (modeLabel) {
                modeLabel.innerText = "Break Time 😌";
            }

        } else {

            isBreak = false;
            time = focusDuration * 60;

            if (soundEnabled) {
                focusStartSound.play();
            }

            if (modeLabel) {
                modeLabel.innerText = "Focus Time 🎯";
            }
        }

        displayTime();
        startTimer();
    }

    // =========================
    // CSRF
    // =========================
    function getCookie(name) {
        let cookieValue = null;

        document.cookie.split(";").forEach(cookie => {
            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.split("=")[1]);
            }
        });

        return cookieValue;
    }

    // =========================
    // INIT
    // =========================
    displayTime();

    window.startTimer = startTimer;
    window.pauseTimer = pauseTimer;
    window.resetTimer = resetTimer;

});