// book-details.js - book-details.html?id=B001
document.addEventListener("DOMContentLoaded", async () => {
  if (!initShell("browse")) return;

  const status = document.getElementById("detail-status");
  const box = document.getElementById("detail");
  const id = new URLSearchParams(window.location.search).get("id");
  if (!id) {
    status.innerHTML = '<div class="notice error">No book was chosen. <a href="browse-books.html">Browse books</a></div>';
    return;
  }
  status.innerHTML = '<div class="spinner" role="status" aria-label="Loading"></div>';

  async function load() {
    status.innerHTML = '<div class="spinner" role="status" aria-label="Loading"></div>';
    box.style.display = "none";
    try {
      const b = await Api.getBook(id);
      status.innerHTML = "";
      box.style.display = "block";
      const keywords = String(b.keywords || "").split(",").map((k) => k.trim()).filter(Boolean)
        .map((k) => `<span class="tag">${escapeHtml(k)}</span>`).join("");
      box.innerHTML = `
        <div class="detail-grid">
          <div>
            <img class="cover" src="${escapeHtml(coverUrl(b))}" alt="Cover of ${escapeHtml(b.title)}">
            <p class="badge badge-success" style="margin-top:.8rem">Available in library</p>
          </div>
          <div>
            <h1>${escapeHtml(b.title)}</h1>
            <dl class="detail-list">
              <dt>Author</dt><dd>${escapeHtml(b.author)}</dd>
              <dt>Category</dt><dd>${escapeHtml(b.category)}</dd>
              <dt>Subject</dt><dd>${escapeHtml(b.subject)}</dd>
              <dt>Book ID</dt><dd>${escapeHtml(b.bookId)}</dd>
              <dt>Keywords</dt><dd>${keywords}</dd>
              ${b.matchPercent != null ? `<dt>Match Score</dt><dd>${b.matchPercent}% - relevant to your interests</dd>` : ""}
            </dl>
            <p>${escapeHtml(b.description)}</p>
            <div class="form-grid" style="max-width:320px;margin-top:1rem">
              <div class="field"><label for="rating">Rating (optional)</label>
                <select id="rating"><option value="">No rating</option><option value="5">5 - Excellent</option><option value="4">4 - Good</option><option value="3">3 - Okay</option><option value="2">2 - Poor</option><option value="1">1 - Bad</option></select></div>
            </div>
            <div class="field-row" style="margin-top:1rem;gap:.7rem">
              <button class="btn" id="select-btn">Select Book</button>
              <button class="btn btn-outline" id="history-btn">Add to Reading History</button>
              <a class="btn btn-ghost" href="browse-books.html">Back to Browse Books</a>
            </div>
          </div>
        </div>`;

      async function save(button) {
        const rating = document.getElementById("rating").value;
        button.disabled = true; const original = button.textContent; button.textContent = "Saving...";
        try {
          await Api.addHistory({ studentId: Store.get().studentId, bookId: b.bookId, ...(rating ? { rating: Number(rating) } : {}) });
          toast("Saved to your reading history.", "success");
          document.getElementById("select-btn").textContent = "Selected";
          document.getElementById("history-btn").textContent = "Added";
        } catch (err) {
          toast(err.message, "error");
          button.disabled = false; button.textContent = original;
        }
      }
      document.getElementById("select-btn").addEventListener("click", (e) => save(e.target));
      document.getElementById("history-btn").addEventListener("click", (e) => save(e.target));
    } catch (err) {
      box.style.display = "none";
      status.innerHTML = `<div class="notice error">${escapeHtml(err.message)} <button class="btn btn-sm btn-outline" id="retry-btn" style="margin-left:.5rem">Retry</button></div>`;
      document.getElementById("retry-btn").addEventListener("click", load);
    }
  }
  load();
});
