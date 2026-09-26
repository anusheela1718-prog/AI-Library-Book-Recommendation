// dashboard.js
document.addEventListener("DOMContentLoaded", async () => {
  const user = initShell("home");
  if (!user) return;
  document.getElementById("welcome-name").textContent = "Welcome back, " + (user.name || user.studentId).split(" ")[0] + "!";

  const statGrid = document.getElementById("stat-grid");
  const recStatus = document.getElementById("rec-status");
  const recPreview = document.getElementById("rec-preview");

  function setStat(index, value) {
    statGrid.children[index].querySelector(".num").textContent = value;
  }

  recStatus.innerHTML = '<div class="spinner" role="status" aria-label="Loading"></div>';
  try {
    const [booksData, recData, historyData] = await Promise.all([
      Api.getBooks(),
      Api.recommend({ studentId: user.studentId, interests: user.interests, subjects: user.subjects }),
      Api.getHistory(user.studentId),
    ]);
    setStat(0, booksData.count);
    setStat(1, recData.recommendations.length);
    setStat(2, historyData.count);
    setStat(3, (user.interests || []).length + (user.subjects || []).length);

    recStatus.innerHTML = "";
    if (!recData.recommendations.length) {
      recPreview.innerHTML = `<div class="state"><h3>No recommendations yet</h3><p>${escapeHtml(recData.message || "Update your interests to get started.")}</p><a class="btn" href="profile.html">Edit Interests</a></div>`;
    } else {
      recPreview.innerHTML = recData.recommendations.slice(0, 4).map(bookCardHtml).join("");
    }
  } catch (err) {
    recStatus.innerHTML = `<div class="notice error">${escapeHtml(err.message)} <button class="btn btn-sm btn-outline" id="retry-btn" style="margin-left:.5rem">Retry</button></div>`;
    document.getElementById("retry-btn").addEventListener("click", () => window.location.reload());
  }

  recPreview.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-select]");
    if (btn) await selectBook(btn.dataset.select, btn);
  });
});
