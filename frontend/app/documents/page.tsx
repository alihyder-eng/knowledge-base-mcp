"use client";

import {
  ChangeEvent,
  useEffect,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  DocumentItem,
  getDocuments,
  uploadDocument,
  deleteDocument,
} from "@/lib/api";

export default function DocumentsPage() {
  const router = useRouter();

  const [documents, setDocuments] =
    useState<DocumentItem[]>([]);

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [uploading, setUploading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");

  useEffect(() => {
    loadDocuments();
  }, []);

  async function loadDocuments() {
    const token =
      localStorage.getItem(
        "access_token"
      );

    if (!token) {
      router.replace("/login");
      return;
    }

    try {
      setLoading(true);

      const data =
        await getDocuments(token);

      setDocuments(
        data.documents
      );
    } catch (err: any) {
      if (
        err.message
          ?.toLowerCase()
          .includes("unauthorized")
      ) {
        localStorage.removeItem(
          "access_token"
        );

        router.replace("/login");
        return;
      }

      setError(
        err.message ||
          "Could not load documents."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>
  ) {
    setError("");
    setMessage("");

    const file =
      event.target.files?.[0];

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const extension =
      "." +
      file.name
        .split(".")
        .pop()
        ?.toLowerCase();

    if (
      ![".pdf", ".md", ".txt"].includes(
        extension
      )
    ) {
      setSelectedFile(null);
      event.target.value = "";

      setError(
        "Only PDF, MD, and TXT files are supported."
      );

      return;
    }

    setSelectedFile(file);
  }

  async function handleUpload() {
    const token =
      localStorage.getItem(
        "access_token"
      );

    if (!token) {
      router.replace("/login");
      return;
    }

    if (!selectedFile) {
      setError(
        "Please select a document."
      );

      return;
    }

    try {
      setUploading(true);
      setError("");
      setMessage("");

      await uploadDocument(
        token,
        selectedFile
      );

      setMessage(
        "Document uploaded successfully."
      );

      setSelectedFile(null);

      const input =
        document.getElementById(
          "file-input"
        ) as HTMLInputElement | null;

      if (input) {
        input.value = "";
      }

      await loadDocuments();
    } catch (err: any) {
      setError(
        err.message ||
          "Document upload failed."
      );
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(
    documentId: number,
    filename: string
  ) {
    const confirmed =
      window.confirm(
        `Delete "${filename}"?`
      );

    if (!confirmed) {
      return;
    }

    const token =
      localStorage.getItem(
        "access_token"
      );

    if (!token) {
      router.replace("/login");
      return;
    }

    try {
      setError("");
      setMessage("");

      await deleteDocument(
        token,
        documentId
      );

      setMessage(
        "Document deleted successfully."
      );

      setDocuments((current) =>
        current.filter(
          (document) =>
            document.id !== documentId
        )
      );
    } catch (err: any) {
      setError(
        err.message ||
          "Document deletion failed."
      );
    }
  }

  function logout() {
    localStorage.removeItem(
      "access_token"
    );

    router.replace("/login");
  }

  return (
    <main className="app-page">
      <nav className="navbar">
        <div className="nav-brand">
          Personal KB
        </div>

        <div className="nav-links">
          <Link href="/dashboard">
            Dashboard
          </Link>

          <Link
            href="/documents"
            className="active-link"
          >
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
            <h1>
              Documents
            </h1>

            <p className="muted">
              Keep the material you want
              your knowledge base to
              remember in one place.
            </p>
          </div>
        </div>

        <div className="section-card upload-card">
          <div className="section-header">
            <div>
              <h2>
                Add a document
              </h2>

              <p className="muted">
                PDF, Markdown, and text
                files are supported.
              </p>
            </div>
          </div>

          <div className="upload-controls">
            <input
              id="file-input"
              type="file"
              accept=".pdf,.md,.txt"
              onChange={
                handleFileChange
              }
            />

            <button
              type="button"
              onClick={handleUpload}
              disabled={
                uploading ||
                !selectedFile
              }
              className="primary-button"
            >
              {uploading
                ? "Uploading..."
                : "Upload"}
            </button>
          </div>

          {selectedFile && (
            <div className="selected-file">
              <strong>
                {selectedFile.name}
              </strong>
            </div>
          )}

          {error && (
            <div className="error">
              {error}
            </div>
          )}

          {message && (
            <div className="success">
              {message}
            </div>
          )}
        </div>

        <div className="section-card">
          <div className="section-header">
            <h2>
              Your documents
            </h2>

            <span className="count-badge">
              {documents.length}
            </span>
          </div>

          {loading ? (
            <div className="empty-state">
              Loading documents...
            </div>
          ) : documents.length ===
            0 ? (
            <div className="empty-state">
              <h3>
                Nothing here yet
              </h3>

              <p className="muted">
                Upload a document above
                and it will appear here
                once it has been added to
                your knowledge base.
              </p>
            </div>
          ) : (
            <div className="document-list">
              {documents.map(
                (document) => (
                  <div
                    className="document-row"
                    key={document.id}
                  >
                    <div className="document-info">
                      <strong>
                        {document.filename}
                      </strong>

                      <span>
                        {document.file_type.toUpperCase()}
                      </span>

                      <small>
                        Added{" "}
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

                    <button
                      type="button"
                      className="danger-button"
                      onClick={() =>
                        handleDelete(
                          document.id,
                          document.filename
                        )
                      }
                    >
                      Delete
                    </button>
                  </div>
                )
              )}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

