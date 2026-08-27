"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] =
    useState("");
  const [password, setPassword] =
    useState("");
  const [error, setError] =
    useState("");
  const [loading, setLoading] =
    useState(false);

  useEffect(() => {
    const token =
      localStorage.getItem("access_token");

    if (token) {
      router.replace("/dashboard");
    }
  }, [router]);

  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault();

    setError("");

    if (!email || !password) {
      setError(
        "Email and password are required."
      );
      return;
    }

    try {
      setLoading(true);

      const data = await login(
        email,
        password
      );

      const token =
        data.access_token ||
        data.token;

      if (!token) {
        throw new Error(
          "Login succeeded but no access token was returned."
        );
      }

      localStorage.setItem(
        "access_token",
        token
      );

      router.replace("/dashboard");
    } catch (err: any) {
      setError(
        err.message ||
          "Login failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-card">
        <div className="brand">
          Personal Knowledge Base
        </div>

        <h1>Welcome back</h1>

        <p className="muted">
          Login to access your documents
          and search your knowledge base.
        </p>

        <form
          onSubmit={handleSubmit}
          className="form"
        >
          <label>Email</label>

          <input
            type="email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            placeholder="you@example.com"
            autoComplete="email"
          />

          <label>Password</label>

          <input
            type="password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            placeholder="Password"
            autoComplete="current-password"
          />

          {error && (
            <div className="error">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="primary-button"
          >
            {loading
              ? "Logging in..."
              : "Login"}
          </button>
        </form>

        <p className="auth-footer">
          Don't have an account?{" "}
          <Link href="/signup">
            Create an account
          </Link>
        </p>
      </div>
    </main>
  );
}