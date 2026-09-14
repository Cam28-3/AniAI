import { useState } from "react";
import { login, setStoredToken, signup } from "./api";

// Combined login/signup form. Calls onAuthenticated(user) after a successful signup/login and
// after the token has already been persisted to localStorage.
function Auth({ onAuthenticated, onCancel }) {
  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const action = mode === "login" ? login : signup;
      const data = await action(email, password);
      setStoredToken(data.access_token);
      onAuthenticated(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-panel">
      <form onSubmit={handleSubmit} className="auth-form">
        <h2>{mode === "login" ? "Log in" : "Sign up"}</h2>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          minLength={8}
          required
        />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "..." : mode === "login" ? "Log in" : "Sign up"}
        </button>
        <button
          type="button"
          className="auth-switch"
          onClick={() => setMode(mode === "login" ? "signup" : "login")}
        >
          {mode === "login" ? "Need an account? Sign up" : "Have an account? Log in"}
        </button>
        {onCancel && (
          <button type="button" className="auth-cancel" onClick={onCancel}>
            Cancel
          </button>
        )}
      </form>
    </div>
  );
}

export default Auth;
