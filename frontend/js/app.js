// app.js - shared helpers used across every page (Store, escaping, toast, book cards).

// The logged-in student's profile, kept in sync with Auth by nav.js on every protected page.
const Store = {
  get() { try { return JSON.parse(localStorage.getItem("ailib_student")) || null; } catch (e) { return null; } },
  set(student) { localStorage.setItem("ailib_student", JSON.stringify(student)); },
  clear() { localStorage.removeItem("ailib_student"); },
};

const INTERESTS = ["Java", "Python", "AI", "Machine Learning", "Web Development", "Cyber Security",
                   "Data Science", "Cloud Computing", "Database", "Software Engineering"];
const SUBJECTS = ["Programming", "Web Development", "Databases", "Networking", "Systems",
                  "Data Structures and Algorithms", "Artificial Intelligence", "Data Science",
                  "Cyber Security", "Cloud Computing", "Software Engineering", "Emerging Technologies",
                  "Computer Architecture"];

function escapeHtml(text) {
  return String(text == null ? "" : text).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function coverUrl(book) {
  const url = book.imageUrl || "";
  return url || "images/" + encodeURIComponent(book.bookId) + ".svg";
}

function toast(message, type) {
  let el = document.getElementById("toast");
  if (!el) { el = document.createElement("div"); el.id = "toast"; document.body.appendChild(el); }
  el.textContent = message;
  el.className = type || "";
  el.style.display = "block";
  clearTimeout(toast._t);
  toast._t = setTimeout(() => { el.style.display = "none"; }, 3500);
}

function chipsHtml(name, values, checked) {
  return values.map((v) => `
    <label class="chip"><input type="checkbox" name="${name}" value="${escapeHtml(v)}" ${checked.includes(v) ? "checked" : ""}>
    <span>${escapeHtml(v)}</span></label>`).join("");
}

function checkedValues(name) {
  return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map((i) => i.value);
}

// ---------- select a book (used on browse / recommendations / details pages) ----------
async function selectBook(bookId, button) {
  const student = Store.get();
  if (!student) { toast("Please sign in first.", "error"); return false; }
  if (button) { button.disabled = true; button.textContent = "Saving..."; }
  try {
    await Api.addHistory({ studentId: student.studentId, bookId: bookId });
    toast("Saved to your reading history.", "success");
    if (button) button.textContent = "Selected";
    return true;
  } catch (err) {
    toast(err.message, "error");
    if (button) { button.disabled = false; button.textContent = "Select Book"; }
    return false;
  }
}

function bookCardHtml(book) {
  return `
    <article class="book-card">
      <img class="cover" src="${escapeHtml(coverUrl(book))}" alt="Cover of ${escapeHtml(book.title)}" loading="lazy">
      <div class="body">
        <h3>${escapeHtml(book.title)}</h3>
        <p class="meta">${escapeHtml(book.author)}</p>
        <p class="meta"><span class="tag">${escapeHtml(book.category)}</span><span class="tag">${escapeHtml(book.subject)}</span></p>
        <p class="desc" style="font-size:.85rem">${escapeHtml((book.description || "").slice(0, 90))}${(book.description || "").length > 90 ? "..." : ""}</p>
        <div class="card-actions">
          <a class="btn btn-outline btn-sm" href="book-details.html?id=${encodeURIComponent(book.bookId)}">View Details</a>
          <button class="btn btn-sm" data-select="${escapeHtml(book.bookId)}">Select Book</button>
        </div>
      </div>
    </article>`;
}
