// history.js - history.html
document.addEventListener("DOMContentLoaded", async () => {
  const user = initShell("history");
  if (!user) return;

  const status = document.getElementById("history-status");
  const list = document.getElementById("history-list");
  const countLabel = document.getElementById("history-count");
  const search = document.getElementById("history-search");
  let allHistory = [];

  function render() {
    const q = search.value.trim().toLowerCase();
    const items = q ? allHistory.filter((h) => (h.title || "").toLowerCase().includes(q) || (h.author || "").toLowerCase().includes(q)) : allHistory;
    countLabel.textContent = allHistory.length + " book(s)";
    if (!items.length) {
      list.innerHTML = "";
      status.innerHTML = allHistory.length
        ? '<div class="state"><h3>No matches</h3><p>Try a different search word.</p></div>'
        : '<div class="state"><h3>No reading history yet</h3><p>Select a book from Browse Books or Recommendations to see it here.</p><a class="btn" href="browse-books.html">Browse Books</a></div>';
      return;
    }
    status.innerHTML = "";
    list.innerHTML = items.map((h) => `
      <div class="history-item card">
        <img src="${escapeHtml(coverUrl({ imageUrl: h.imageUrl, bookId: h.bookId }))}" alt="">
        <div>
          <strong>${escapeHtml(h.title || h.bookId)}</strong>
          <p class="meta">${escapeHtml(h.author || "")} &middot; ${escapeHtml(h.category || "")}</p>
          <p class="meta">Selected ${escapeHtml(new Date(h.selectedAt).toLocaleDateString())}${h.rating ? " &middot; Rating: " + h.rating + "/5" : ""}</p>
        </div>
        <a class="btn btn-outline btn-sm" href="book-details.html?id=${encodeURIComponent(h.bookId)}">View Details</a>
      </div>`).join("");
  }

  async function load() {
    status.innerHTML = '<div class="spinner" role="status" aria-label="Loading"></div>';
    try {
      const data = await Api.getHistory(user.studentId);
      allHistory = data.history;
      render();
    } catch (err) {
      status.innerHTML = `<div class="notice error">${escapeHtml(err.message)} <button class="btn btn-sm btn-outline" id="retry-btn" style="margin-left:.5rem">Retry</button></div>`;
      document.getElementById("retry-btn").addEventListener("click", load);
    }
  }
  search.addEventListener("input", render);
  load();
});
