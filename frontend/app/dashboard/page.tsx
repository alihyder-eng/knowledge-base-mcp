"use client";

import {
  useEffect,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  DocumentItem,
  User,
  getDocuments,
  getMe,
} from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();

  const [user, setUser] =
    useState<User | null>(null);

  const [documents, setDocuments] =
    useState<DocumentItem[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    async function loadDashboard() {
      const token =
        localStorage.getItem(
          "access_token"
        );

      if (!token) {
        router.replace("/login");
        return;
      }

      try {
        const [userData, documentData] =
          await Promise.all([
            getMe(token),
            getDocuments(token),
          ]);

        setUser(userData);
        setDocuments(
          documentData.documents
        );
      } catch (err: any) {
        localStorage.removeItem(
          "access_token"
        );

        router.replace("/login");

        setError(
          err.message ||
            "Unable to load dashboard."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, [router]);

  function logout() {
    localStorage.removeItem(
      "access_token"
    );

    router.replace("/login");
  }

  if (loading) {
    return (
      <main className="center-page">
        <div className="loading-card">
          Loading dashboard...
        </div>
      </main>
    );
  }

  return (
    <main className="app-page">
      <nav className="navbar">
        <div className="nav-brand">
          Personal KB
        </div>

        <div className="nav-links">
          <Link
            href="/dashboard"
            className="active-link"
          >
            Dashboard
          </Link>

          <Link href="/documents">
            Documents
          </Link>

          <Link href="/search">
            Search
          </Link>

          <button
            type="button"
            onClick={logout}
            className="logout-button"
          >
            Logout
          </button>
        </div>
      </nav>

      <section className="content">
        <div className="page-header">
          <div>
            <h1>Dashboard</h1>

            <p className="muted">
              {user?.email}
            </p>
          </div>

          <Link
            href="/documents"
            className="primary-button link-button"
          >
            Upload document
          </Link>
        </div>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <div className="stats-grid">
          <div className="stat-card">
            <span>
              Documents
            </span>

            <strong>
              {documents.length}
            </strong>
          </div>

          <div className="stat-card">
            <span>
              Knowledge Base
            </span>

            <strong>
              {documents.length > 0
                ? "Active"
                : "Empty"}
            </strong>
          </div>
        </div>

        <div className="section-card">
          <div className="section-header">
            <h2>
              Your documents
            </h2>

            <Link href="/documents">
              Manage documents
            </Link>
          </div>

          {documents.length === 0 ? (
            <div className="empty-state">
              <h3>
                Your knowledge base is empty
              </h3>

              <p className="muted">
                Add your first document to
                make your notes and resources
                searchable from one place.
              </p>

              <Link
                href="/documents"
                className="primary-button link-button"
              >
                Upload a document
              </Link>
            </div>
          ) : (
            <div className="document-list">
              {documents
                .slice(0, 5)
                .map((document) => (
                  <div
                    className="document-row"
                    key={document.id}
                  >
                    <div>
                      <strong>
                        {document.filename}
                      </strong>

                      <span>
                        {document.file_type.toUpperCase()}
                      </span>
                    </div>

                    <small>
                      {new Date(
                        document.created_at
                      ).toLocaleDateString(
                        undefined,
                        {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                        }
                      )}
                    </small>
                  </div>
                ))}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

