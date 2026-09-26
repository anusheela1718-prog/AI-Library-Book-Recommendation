// signup.js
document.addEventListener("DOMContentLoaded", () => {
  if (Auth.isLoggedIn()) { window.location.href = "dashboard.html"; return; }

  document.getElementById("interest-chips").innerHTML = chipsHtml("interest", INTERESTS, []);
  document.getElementById("subject-chips").innerHTML = chipsHtml("subject", SUBJECTS, []);

  document.getElementById("signup-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorBox = document.getElementById("form-error");
    errorBox.style.display = "none";

    const studentId = document.getElementById("studentId").value.trim();
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const department = document.getElementById("department").value.trim();
    const year = document.getElementById("year").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const extraList = document.getElementById("extraInterests").value.split(",").map((t) => t.trim()).filter(Boolean);
    const interests = checkedValues("interest").concat(extraList);
    const subjects = checkedValues("subject");

    let problem = "";
    if (!/^[A-Za-z0-9_-]{1,20}$/.test(studentId)) problem = "Student ID may contain only letters, numbers, - and _ (max 20 characters).";
    else if (!name) problem = "Please enter your full name.";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) problem = "Please enter a valid email address.";
    else if (password.length < 6) problem = "Password must be at least 6 characters.";
    else if (password !== confirmPassword) problem = "Passwords do not match.";
    else if (!interests.length && !subjects.length) problem = "Please select at least one interest or subject.";
    if (problem) { errorBox.textContent = problem; errorBox.style.display = "block"; return; }

    const button = document.getElementById("submit-btn");
    button.disabled = true; button.textContent = "Creating account...";
    const student = { studentId, name, department, year, interests, subjects };
    try {
      await Api.saveStudent(student);      // real backend save (DynamoDB) - used by the recommendation engine
      Auth.register(Object.assign({ email, password }, student));  // local demo login record
      Auth.login(studentId, password, true);
      Store.set(student);
      window.location.href = "dashboard.html";
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.style.display = "block";
      button.disabled = false; button.textContent = "Create Account";
    }
  });
});
