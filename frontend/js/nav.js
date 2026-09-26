// nav.js - builds the shared top navigation + footer on every protected page,
// and enforces login. Include AFTER auth.js and BEFORE the page's own script.
function initShell(activeKey) {
  Auth.requireAuth();
  const user = Auth.currentUser();
  if (!user) { Auth.logout(); return; }
  Store.set(user); // keep js/app.js (Api calls) in sync with the logged-in student

  const initials = (user.name || user.studentId || "?").trim().slice(0, 1).toUpperCase();
  const link = (href, text, key) => `<a href="${href}" class="${activeKey === key ? "active" : ""}">${text}</a>`;

  document.getElementById("navbar").innerHTML = `
    <nav class="topnav"><div class="container">
      <a class="brand" href="dashboard.html"><span class="mark">AI</span>Library</a>
      <button class="nav-toggle" id="nav-toggle" aria-label="Menu" aria-expanded="false">&#9776;</button>
      <div class="nav-links" id="nav-links">
        ${link("dashboard.html", "Home", "home")}
        ${link("browse-books.html", "Browse Books", "browse")}
        ${link("recommendations.html", "Recommendations", "rec")}
        ${link("history.html", "Reading History", "history")}
        ${link("profile.html", "Profile", "profile")}
        ${link("about.html", "About", "about")}
      </div>
      <div class="nav-user">
        <div class="avatar" aria-hidden="true">${escapeHtml(initials)}</div>
        <div class="who"><strong>${escapeHtml(user.name || user.studentId)}</strong>${escapeHtml(user.studentId)}</div>
        <button class="nav-logout" id="logout-btn">Log out</button>
      </div>
    </div></nav>`;

  document.getElementById("footer").innerHTML =
    `<div class="container">AI Library &middot; Final Year BCA Project &middot; <a href="about.html">How recommendations work</a></div>`;

  document.getElementById("nav-toggle").addEventListener("click", () => {
    const links = document.getElementById("nav-links");
    const open = links.classList.toggle("open");
    document.getElementById("nav-toggle").setAttribute("aria-expanded", open);
  });
  document.getElementById("logout-btn").addEventListener("click", Auth.logout.bind(Auth));
  return user;
}
