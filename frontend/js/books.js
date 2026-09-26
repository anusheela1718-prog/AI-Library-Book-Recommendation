// books.js - browse-books.html
document.addEventListener("DOMContentLoaded", () => {
  if (!initShell("browse")) return;

  const grid = document.getElementById("browse-grid");
  const search = document.getElementById("browse-search");
  const category = document.getElementById("browse-category");
  const sort = document.getElementById("browse-sort");
  const status = document.getElementById("browse-status");
  const resultCount = document.getElementById("result-count");
  let allBooksLoaded = false;

  function sortBooks(books) {
    const key = sort.value;
    return [...books].sort((a, b) => (a[key] || "").localeCompare(b[key] || ""));
  }

  async function load() {
    status.innerHTML = '<div class="spinner" role="status" aria-label="Loading"></div>';
    grid.innerHTML = "";
    try {
      const params = {};
      if (search.value.trim()) params.q = search.value.trim();
      if (category.value) params.category = category.value;
      const data = await Api.getBooks(params);

      if (!allBooksLoaded) {
        const all = await Api.getBooks();
        [...new Set(all.books.map((b) => b.category))].sort().forEach((c) => {
          const o = document.createElement("option"); o.value = c; o.textContent = c; category.appendChild(o);
        });
        allBooksLoaded = true;
      }
      resultCount.textContent = data.count + " books";
      status.innerHTML = data.count ? "" : '<div class="state"><h3>No books found</h3><p>Try a different search word or category.</p></div>';
      grid.innerHTML = sortBooks(data.books).map(bookCardHtml).join("");
    } catch (err) {
      status.innerHTML = `<div class="notice error">${escapeHtml(err.message)} <button class="btn btn-sm btn-outline" id="retry-btn" style="margin-left:.5rem">Retry</button></div>`;
      document.getElementById("retry-btn").addEventListener("click", load);
    }
  }

  let timer;
  search.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(load, 300); });
  category.addEventListener("change", load);
  sort.addEventListener("change", load);
  grid.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-select]");
    if (btn) await selectBook(btn.dataset.select, btn);
  });
  load();
});
