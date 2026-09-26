// login.js
document.addEventListener("DOMContentLoaded", () => {
  if (Auth.isLoggedIn()) { window.location.href = "dashboard.html"; return; }

  document.getElementById("pw-toggle").addEventListener("click", () => {
    const field = document.getElementById("password");
    const show = field.type === "password";
    field.type = show ? "text" : "password";
    document.getElementById("pw-toggle").textContent = show ? "Hide" : "Show";
  });

  document.getElementById("forgot-link").addEventListener("click", (e) => {
    e.preventDefault();
    toast("This is a demo login - there is no password reset. Please sign up again if needed.", "info");
  });

  document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorBox = document.getElementById("form-error");
    errorBox.style.display = "none";
    const id = document.getElementById("loginId").value.trim();
    const password = document.getElementById("password").value;
    const remember = document.getElementById("remember").checked;
    if (!id || !password) {
      errorBox.textContent = "Please enter your Student ID / email and password.";
      errorBox.style.display = "block";
      return;
    }
    const button = document.getElementById("submit-btn");
    button.disabled = true; button.textContent = "Signing in...";
    try {
      const user = Auth.login(id, password, remember);
      // Pull the latest saved profile from the backend (source of truth for interests/subjects).
      try {
        const fresh = await Api.getStudent(user.studentId);
        Store.set(Object.assign({}, user, fresh));
      } catch (err) {
        Store.set(user); // backend not reachable yet - fall back to the locally stored profile
      }
      window.location.href = "dashboard.html";
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.style.display = "block";
      button.disabled = false; button.textContent = "Sign In";
    }
  });
});
