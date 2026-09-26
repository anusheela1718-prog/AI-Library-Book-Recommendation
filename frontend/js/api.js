// api.js - all calls to the backend (API Gateway + Lambda) live here.
const API_BASE = ((window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL) || "").replace(/\/$/, "");

async function apiRequest(method, path, body) {
  const options = { method, headers: {} };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  let response;
  try {
    response = await fetch(API_BASE + path, options);
  } catch (err) {
    // network down, wrong API URL, or CORS not enabled
    throw new Error("Cannot reach the server. Check your internet connection and the API URL in js/config.js.");
  }
  let data = null;
  try { data = await response.json(); } catch (err) { /* response was not JSON */ }
  if (!response.ok) {
    throw new Error((data && (data.error || data.message)) || "Request failed (status " + response.status + ").");
  }
  return data;
}

const Api = {
  health: () => apiRequest("GET", "/health"),
  getBooks: (params) => apiRequest("GET", "/books" + (params ? "?" + new URLSearchParams(params) : "")),
  getBook: (id) => apiRequest("GET", "/books/" + encodeURIComponent(id)),
  saveStudent: (student) => apiRequest("POST", "/students", student),
  getStudent: (id) => apiRequest("GET", "/students/" + encodeURIComponent(id)),
  recommend: (payload) => apiRequest("POST", "/recommendations", payload),
  addHistory: (payload) => apiRequest("POST", "/history", payload),
  getHistory: (id) => apiRequest("GET", "/history/" + encodeURIComponent(id)),
};
