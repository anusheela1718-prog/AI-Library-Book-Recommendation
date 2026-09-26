// profile.js - profile.html
document.addEventListener("DOMContentLoaded", () => {
  const user = initShell("profile");
  if (!user) return;

  const initials = (user.name || user.studentId || "?").trim().slice(0, 1).toUpperCase();
  document.getElementById("profile-avatar").textContent = initials;
  document.getElementById("profile-name").textContent = user.name || user.studentId;
  document.getElementById("profile-id").textContent = user.studentId;
  document.getElementById("v-email").textContent = user.email || "-";
  document.getElementById("v-department").textContent = user.department || "-";
  document.getElementById("v-year").textContent = user.year ? user.year + (["","st","nd","rd"][user.year] || "th") + " year" : "-";
  document.getElementById("v-interests").innerHTML = (user.interests || []).map((i) => `<span class="tag">${escapeHtml(i)}</span>`).join("") || "-";
  document.getElementById("v-subjects").innerHTML = (user.subjects || []).map((s) => `<span class="tag">${escapeHtml(s)}</span>`).join("") || "-";

  const viewMode = document.getElementById("view-mode");
  const editForm = document.getElementById("edit-form");

  document.getElementById("edit-btn").addEventListener("click", () => {
    document.getElementById("e-name").value = user.name || "";
    document.getElementById("e-department").value = user.department || "";
    document.getElementById("e-year").value = user.year || "3";
    document.getElementById("e-interest-chips").innerHTML = chipsHtml("e-interest", INTERESTS, user.interests || []);
    document.getElementById("e-subject-chips").innerHTML = chipsHtml("e-subject", SUBJECTS, user.subjects || []);
    document.getElementById("e-extra").value = (user.interests || []).filter((i) => !INTERESTS.includes(i)).join(", ");
    viewMode.style.display = "none";
    editForm.style.display = "block";
  });
  document.getElementById("cancel-btn").addEventListener("click", () => {
    editForm.style.display = "none";
    viewMode.style.display = "block";
  });
  document.getElementById("logout-btn2").addEventListener("click", () => Auth.logout());

  editForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorBox = document.getElementById("edit-error");
    errorBox.style.display = "none";
    const extraList = document.getElementById("e-extra").value.split(",").map((t) => t.trim()).filter(Boolean);
    const interests = checkedValues("e-interest").concat(extraList);
    const subjects = checkedValues("e-subject");
    const name = document.getElementById("e-name").value.trim();
    if (!name) { errorBox.textContent = "Please enter your name."; errorBox.style.display = "block"; return; }
    if (!interests.length && !subjects.length) { errorBox.textContent = "Please select at least one interest or subject."; errorBox.style.display = "block"; return; }

    const button = document.getElementById("save-btn");
    button.disabled = true; button.textContent = "Saving...";
    const updated = Object.assign({}, user, {
      name, department: document.getElementById("e-department").value.trim(),
      year: document.getElementById("e-year").value, interests, subjects,
    });
    try {
      await Api.saveStudent({ studentId: updated.studentId, name: updated.name, department: updated.department, year: updated.year, interests, subjects });
      // keep the local demo login record in sync too
      const users = JSON.parse(localStorage.getItem(Auth.USERS_KEY) || "{}");
      users[updated.studentId.toUpperCase()] = updated;
      localStorage.setItem(Auth.USERS_KEY, JSON.stringify(users));
      Store.set(updated);
      toast("Profile updated.", "success");
      window.location.reload();
    } catch (err) {
      errorBox.textContent = err.message; errorBox.style.display = "block";
      button.disabled = false; button.textContent = "Save Changes";
    }
  });
});
