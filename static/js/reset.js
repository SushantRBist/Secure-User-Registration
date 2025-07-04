document.addEventListener("DOMContentLoaded", function () {
  const passwordInput = document.getElementById("new_password");
  const confirmInput = document.getElementById("confirm_password");
  const mismatchMessage = document.getElementById("passwordMismatch");
  const resetBtn = document.getElementById("resetBtn");

  const checks = {
    lowercase: document.getElementById("lowercase"),
    uppercase: document.getElementById("uppercase"),
    number: document.getElementById("number"),
    symbol: document.getElementById("symbol"),
    length: document.getElementById("length")
  };

  document.querySelectorAll(".toggle-password").forEach(cb => {
    cb.addEventListener("change", () => {
      const input = document.getElementById(cb.dataset.target);
      input.type = input.type === "password" ? "text" : "password";
    });
  });

  function isAllChecklistValid() {
    const val = passwordInput.value;
    return (
      /[a-z]/.test(val) &&
      /[A-Z]/.test(val) &&
      /[0-9]/.test(val) &&
      /[^A-Za-z0-9]/.test(val) &&
      val.length >= 8
    );
  }

  function validatePasswords() {
    const pw = passwordInput.value;
    const confirm = confirmInput.value;

    mismatchMessage.style.display = pw && confirm && pw !== confirm ? "block" : "none";
    resetBtn.disabled = !(pw && confirm && pw === confirm && isAllChecklistValid());
  }

  passwordInput.addEventListener("input", () => {
    const val = passwordInput.value;

    checks.lowercase.classList.toggle("valid", /[a-z]/.test(val));
    checks.uppercase.classList.toggle("valid", /[A-Z]/.test(val));
    checks.number.classList.toggle("valid", /[0-9]/.test(val));
    checks.symbol.classList.toggle("valid", /[^A-Za-z0-9]/.test(val));
    checks.length.classList.toggle("valid", val.length >= 8);

    for (const key in checks) {
      checks[key].classList.toggle("invalid", !checks[key].classList.contains("valid"));
      checks[key].textContent =
        (checks[key].classList.contains("valid") ? "✅ " : "❌ ") + checks[key].textContent.slice(2);
    }

    validatePasswords();
  });

  confirmInput.addEventListener("input", validatePasswords);
});
