document.addEventListener("DOMContentLoaded", function () {
  const countdownElement = document.getElementById("countdown-timer");

  // Get countdownSeconds from the inline script
  if (countdownElement && window.countdownSeconds) {
    let secondsLeft = window.countdownSeconds;

    function updateTimer() {
      if (secondsLeft <= 0) {
        countdownElement.textContent = "You can now try logging in again.";
        return;
      }

      const minutes = Math.floor(secondsLeft / 60);
      const seconds = secondsLeft % 60;
      countdownElement.textContent = `${minutes}m ${seconds}s`;
      secondsLeft--;

      setTimeout(updateTimer, 1000);
    }

    updateTimer();
  }
});

document.addEventListener("DOMContentLoaded", function () {
  // Existing countdown code 
  const countdownElement = document.getElementById("countdown-timer");
  if (countdownElement && window.countdownSeconds) {
    let secondsLeft = window.countdownSeconds;
    function updateTimer() {
      if (secondsLeft <= 0) {
        countdownElement.textContent = "You can now try logging in again.";
        return;
      }
      const minutes = Math.floor(secondsLeft / 60);
      const seconds = secondsLeft % 60;
      countdownElement.textContent = `${minutes}m ${seconds}s`;
      secondsLeft--;
      setTimeout(updateTimer, 1000);
    }
    updateTimer();
  }

  //  show/hide password logic
  const checkbox = document.querySelector(".toggle-password");
  if (checkbox) {
    const targetId = checkbox.dataset.target;
    const passwordField = document.getElementById(targetId);
    if (passwordField) {
      checkbox.addEventListener("change", function () {
        passwordField.type = this.checked ? "text" : "password";
      });
    }
  }
});
