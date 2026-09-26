// recommendations.js - recommendations.html
function recCardHtml(book, index) {
  const why = (book.matchedTerms || []).length
    ? `Matches your interest in ${book.matchedTerms.slice(0, 3).map(escapeHtml).join(", ")}.`
    : "Matches your interests and subjects.";
  return `
    <article class="rec-card card">
      <img class="cover" src="${escapeHtml(coverUrl(book))}" alt="Cover of ${escapeHtml(book.title)}">
      <div>
        <div class="rec-head"><span class="rank">${index + 1}.</span><h3>${escapeHtml(book.title)}</h3></div>
        <p class="meta">${escapeHtml(book.author)} &nbsp;&middot;&nbsp; ${escapeHtml(book.category)} &nbsp;&middot;&nbsp; ${escapeHtml(book.subject)}</p>
        <div class="score-row">Similarity: ${book.matchPercent}%
          <div class="bar" aria-hidden="true"><div style="width:${Math.min(100, book.matchPercent)}%"></div></div>
        </div>
        <p class="desc">${escapeHtml(book.description)}</p>
        <p class="why"><b>Why this book:</b> ${why}</p>
        <div class="card-actions">
          <a class="btn btn-outline btn-sm" href="book-details.html?id=${encodeURIComponent(book.bookId)}">View Details</a>
          <button class="btn btn-sm" data-select="${escapeHtml(book.bookId)}">Select Book</button>
        </div>
      </div>
    </article>`;
}

document.addEventListener("DOMContentLoaded", () => {
  const user = initShell("rec");
  if (!user) return;

  async function loadRecommendations() {
    const message = document.getElementById("rec-message");
    const list = document.getElementById("rec-list");
    list.innerHTML = "";
    message.innerHTML = '<div class="spinner" role="status" aria-label="Loading recommendations"></div>';
    try {
      const data = await Api.recommend({ studentId: user.studentId, interests: user.interests, subjects: user.subjects });
      if (!data.recommendations.length) {
        message.innerHTML = `<div class="state"><h3>No recommendations found</h3><p>${escapeHtml(data.message || "Try different interests.")}</p><a class="btn" href="profile.html">Edit Interests</a></div>`;
        return;
      }
      message.innerHTML = data.historyCount
        ? `<div class="notice info">Personalized using your interests and ${data.historyCount} book(s) in your reading history.</div>`
        : "";
      list.innerHTML = data.recommendations.map(recCardHtml).join("");
    } catch (err) {
      message.innerHTML = `<div class="notice error">${escapeHtml(err.message)} <button class="btn btn-sm btn-outline" id="retry-btn" style="margin-left:.5rem">Retry</button></div>`;
      document.getElementById("retry-btn").addEventListener("click", loadRecommendations);
    }
  }

  document.getElementById("refresh-btn").addEventListener("click", loadRecommendations);
  document.getElementById("rec-list").addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-select]");
    if (!btn) return;
    if (await selectBook(btn.dataset.select, btn)) {
      document.getElementById("rec-message").innerHTML =
        '<div class="notice success">Book saved to your history. Click <b>Refresh Recommendations</b> to see results personalized with it.</div>';
    }
  });
  loadRecommendations();
});
