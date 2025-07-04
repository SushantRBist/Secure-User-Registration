const passwordInput = document.getElementById("password");
const confirmInput = document.getElementById("confirm_password");
const matchMessage = document.getElementById("matchMessage");
const registerBtn = document.getElementById("registerBtn");

const checks = {
  lowercase: document.getElementById("lowercase"),
  uppercase: document.getElementById("uppercase"),
  number: document.getElementById("number"),
  symbol: document.getElementById("symbol"),
  length: document.getElementById("length")
};

// Toggle password visibility
document.querySelectorAll(".toggle-password").forEach((checkbox) => {
  checkbox.addEventListener("change", function () {
    const input = document.getElementById(this.dataset.target);
    input.type = input.type === "password" ? "text" : "password";
  });
});

// Check if passwords match
function validatePasswords() {
  const pw = passwordInput.value;
  const confirm = confirmInput.value;

  if (pw && confirm && pw !== confirm) {
    matchMessage.style.display = "block";
    registerBtn.disabled = true;
  } else {
    matchMessage.style.display = "none";
    registerBtn.disabled = !isAllChecklistValid();
  }
}

// Check if all password rules are valid
function isAllChecklistValid() {
  return (
    /[a-z]/.test(passwordInput.value) &&
    /[A-Z]/.test(passwordInput.value) &&
    /[0-9]/.test(passwordInput.value) &&
    /[^A-Za-z0-9]/.test(passwordInput.value) &&
    passwordInput.value.length >= 8
  );
}
// Update checklist on input
passwordInput.addEventListener("input", () => {
  const val = passwordInput.value;

  const tests = {
    lowercase: /[a-z]/.test(val),
    uppercase: /[A-Z]/.test(val),
    number: /[0-9]/.test(val),
    symbol: /[^A-Za-z0-9]/.test(val),
    length: val.length >= 8
  };

  for (const key in tests) {
    if (tests[key]) {
      checks[key].classList.add("valid");
      checks[key].classList.remove("invalid");
      checks[key].textContent = `✅ ${checks[key].textContent.slice(2)}`;
    } else {
      checks[key].classList.add("invalid");
      checks[key].classList.remove("valid");
      checks[key].textContent = `❌ ${checks[key].textContent.slice(2)}`;
    }
  }

  validatePasswords();
});

confirmInput.addEventListener("input", validatePasswords);
