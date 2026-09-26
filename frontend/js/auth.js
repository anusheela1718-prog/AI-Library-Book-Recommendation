// auth.js - DEMO authentication only (runs entirely in the browser with localStorage).
// This is NOT secure and is not production-grade: passwords are stored in plain text in
// the browser, purely so the app has a working Sign In / Sign Up flow to demonstrate the
// multi-page UI. The student profile itself (interests, subjects) is still saved for real
// through Api.saveStudent() into DynamoDB, and recommendations still come from the real
// backend TF-IDF + cosine similarity engine.
const Auth = {
  USERS_KEY: "ailib_users",
  SESSION_KEY: "ailib_session",

  _users() { try { return JSON.parse(localStorage.getItem(this.USERS_KEY)) || {}; } catch (e) { return {}; } },
  _saveUsers(u) { localStorage.setItem(this.USERS_KEY, JSON.stringify(u)); },

  findUser(idOrEmail) {
    const users = this._users();
    const key = (idOrEmail || "").trim().toLowerCase();
    return users[key.toUpperCase()] || Object.values(users).find((u) => (u.email || "").toLowerCase() === key) || null;
  },

  register(user) {
    const users = this._users();
    const id = user.studentId.toUpperCase();
    if (users[id]) throw new Error("This Student ID is already registered. Please sign in instead.");
    if (Object.values(users).some((u) => (u.email || "").toLowerCase() === user.email.toLowerCase())) {
      throw new Error("This email is already registered. Please sign in instead.");
    }
    users[id] = user;
    this._saveUsers(users);
  },

  login(idOrEmail, password, remember) {
    const user = this.findUser(idOrEmail);
    if (!user || user.password !== password) {
      throw new Error("Incorrect Student ID / email or password.");
    }
    const session = { studentId: user.studentId };
    if (remember) localStorage.setItem(this.SESSION_KEY, JSON.stringify(session));
    else sessionStorage.setItem(this.SESSION_KEY, JSON.stringify(session));
    return user;
  },

  getSession() {
    try {
      return JSON.parse(localStorage.getItem(this.SESSION_KEY)) || JSON.parse(sessionStorage.getItem(this.SESSION_KEY));
    } catch (e) { return null; }
  },

  isLoggedIn() { return !!this.getSession(); },

  logout() {
    localStorage.removeItem(this.SESSION_KEY);
    sessionStorage.removeItem(this.SESSION_KEY);
    window.location.href = "login.html";
  },

  // Call at the top of every protected page. Redirects to login if not signed in.
  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = "login.html";
      throw new Error("redirecting to login");
    }
  },

  currentUser() {
    const session = this.getSession();
    if (!session) return null;
    return this.findUser(session.studentId);
  },
};
