"use client";

import {
  FormEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  SearchResult,
  searchDocuments,
} from "@/lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  results?: SearchResult[];
  timestamp: Date;
};

const suggestions = [
  "What are the main topics covered in my documents?",
  "Summarize the most important information from my documents.",
  "What are the key concepts I should remember?",
  "Find the most relevant information about my documents.",
];

export default function SearchPage() {
  const router = useRouter();

  const messagesEndRef =
    useRef<HTMLDivElement>(null);

  const textareaRef =
    useRef<HTMLTextAreaElement>(null);

  const abortRef =
    useRef<AbortController | null>(null);

  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [expandedSources, setExpandedSources] =
    useState<Record<string, boolean>>({});

  const [lastQuery, setLastQuery] =
    useState("");

  /* =====================================================
     AUTHENTICATION
  ===================================================== */

  useEffect(() => {
    const token =
      localStorage.getItem("access_token");

    if (!token) {
      router.replace("/login");
    }
  }, [router]);

  /* =====================================================
     AUTO SCROLL
  ===================================================== */

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  /* =====================================================
     TEXTAREA
  ===================================================== */

  const resizeTextarea = useCallback(() => {
    const textarea =
      textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";

    const height = Math.min(
      textarea.scrollHeight,
      180
    );

    textarea.style.height =
      `${height}px`;
  }, []);

  function handleQueryChange(
    value: string
  ) {
    setQuery(value);

    requestAnimationFrame(() => {
      resizeTextarea();
    });
  }

  function focusInput() {
    requestAnimationFrame(() => {
      textareaRef.current?.focus();
    });
  }

  /* =====================================================
     SEARCH
  ===================================================== */

  async function executeSearch(searchQuery: string) {
  const token =
    localStorage.getItem("access_token");

  if (!token) {
    router.replace("/login");
    return;
  }

  const cleanQuery = searchQuery.trim();

  if (!cleanQuery || loading) {
    return;
  }

  const userMessage: Message = {
    id: `${Date.now()}-user`,
    role: "user",
    content: cleanQuery,
    timestamp: new Date(),
  };

  setMessages((previous) => [
    ...previous,
    userMessage,
  ]);

  setQuery("");
  setError("");
  setLastQuery(cleanQuery);
  setLoading(true);

  if (textareaRef.current) {
    textareaRef.current.style.height = "auto";
  }

  // Create a controller for THIS request
  const controller = new AbortController();

  // Store it so Stop Search can abort it
  abortRef.current = controller;

  try {
    const data = await searchDocuments(
      token,
      cleanQuery,
      topK,
      controller.signal
    );

    const results = data.results ?? [];

    const answer =
      data.answer?.trim() ||
      (
        results.length > 0
          ? "I found relevant information in your documents, but I could not generate an answer."
          : "I couldn't find enough relevant information in your uploaded documents to answer this question."
      );

    const assistantMessage: Message = {
      id: `${Date.now()}-assistant`,
      role: "assistant",
      content: answer,
      results,
      timestamp: new Date(),
    };

    setMessages((previous) => [
      ...previous,
      assistantMessage,
    ]);

    if (results.length > 0) {
      setExpandedSources((previous) => ({
        ...previous,
        [assistantMessage.id]: true,
      }));
    }
  } catch (err: unknown) {
    // User intentionally stopped the request
    if (
      err instanceof DOMException &&
      err.name === "AbortError"
    ) {
      return;
    }

    setError(
      err instanceof Error
        ? err.message
        : "Something went wrong while searching your knowledge base."
    );
  } finally {
    // Only clear the active controller
    if (abortRef.current === controller) {
      abortRef.current = null;
      setLoading(false);
    }

    focusInput();
  }
}

  /* =====================================================
     FORM SUBMIT
  ===================================================== */

  async function handleSearch(
    event?: FormEvent
  ) {
    event?.preventDefault();

    if (
      !query.trim() ||
      loading
    ) {
      return;
    }

    await executeSearch(query);
  }

  /* =====================================================
     STOP SEARCH
  ===================================================== */

  function stopSearch() {
    abortRef.current?.abort();

    abortRef.current = null;

    setLoading(false);

    focusInput();
  }

  /* =====================================================
     LOGOUT
  ===================================================== */

  function logout() {
    localStorage.removeItem(
      "access_token"
    );

    router.replace("/login");
  }

  /* =====================================================
     CLEAR CHAT
  ===================================================== */

  function clearChat() {
    if (loading) {
      stopSearch();
    }

    setMessages([]);
    setError("");
    setLastQuery("");
    setExpandedSources({});
  }

  /* =====================================================
     SUGGESTIONS
  ===================================================== */

  function useSuggestion(
    suggestion: string
  ) {
    setQuery(suggestion);

    requestAnimationFrame(() => {
      resizeTextarea();
      focusInput();
    });
  }

  /* =====================================================
     SOURCE TOGGLE
  ===================================================== */

  function toggleSources(
    messageId: string
  ) {
    setExpandedSources((previous) => ({
      ...previous,
      [messageId]:
        !(previous[messageId] ?? true),
    }));
  }

  /* =====================================================
     SCORE
  ===================================================== */

  function getScoreClass(
    score: number
  ) {
    if (score >= 0.85) {
      return "score-excellent";
    }

    if (score >= 0.7) {
      return "score-strong";
    }

    if (score >= 0.5) {
      return "score-good";
    }

    return "score-low";
  }

  function getScoreLabel(
    score: number
  ) {
    if (score >= 0.85) {
      return "High relevance";
    }

    if (score >= 0.7) {
      return "Good relevance";
    }

    if (score >= 0.5) {
      return "Moderate relevance";
    }

    return "Low relevance";
  }

  /* =====================================================
     TIME
  ===================================================== */

  function formatTime(
    date: Date
  ) {
    return date.toLocaleTimeString(
      [],
      {
        hour: "2-digit",
        minute: "2-digit",
      }
    );
  }

  /* =====================================================
     UI
  ===================================================== */

  return (
    <main className="app-page chatbot-page">

      {/* =================================================
          NAVIGATION
      ================================================= */}

      <nav className="navbar">

        <Link
          href="/dashboard"
          className="nav-brand"
        >
          <span className="brand-mark">
            KB
          </span>

          <span className="brand-name">
            Personal KB
          </span>
        </Link>

        <div className="nav-links">

          <Link href="/dashboard">
            Dashboard
          </Link>

          <Link href="/documents">
            Documents
          </Link>

          <Link
            href="/search"
            className="active-link"
          >
            Chat
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

      {/* =================================================
          CHAT
      ================================================= */}

      <section className="chat-container">

        {/* =================================================
            HEADER
        ================================================= */}

        <header className="chat-header">

          <div className="chat-title-row">

            <div className="bot-avatar">

              <span>
                KB
              </span>

              <span className="online-dot" />

            </div>

            <div className="chat-heading">

              <h1 className="chat-title">
                Personal Knowledge
              </h1>

              <p className="muted">
                Ask questions about your
                documents
              </p>

            </div>

          </div>

          <div className="chat-actions">

            <label className="source-control">

              <span>
                Sources
              </span>

              <select
                value={topK}
                onChange={(event) =>
                  setTopK(
                    Number(
                      event.target.value
                    )
                  )
                }
                className="topk-select"
                disabled={loading}
                aria-label="Number of sources"
              >
                {[1, 2, 3, 4, 5].map(
                  (number) => (
                    <option
                      key={number}
                      value={number}
                    >
                      {number}
                    </option>
                  )
                )}
              </select>

            </label>

            {messages.length > 0 && (
              <button
                type="button"
                onClick={clearChat}
                className="clear-chat-button"
                disabled={loading}
              >

                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M3 6h18"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />

                  <path
                    d="M8 6V4h8v2"
                    stroke="currentColor"
                    strokeWidth="2"
                  />

                  <path
                    d="M19 6l-1 14H6L5 6"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinejoin="round"
                  />
                </svg>

                Clear

              </button>
            )}

          </div>

        </header>

        {/* =================================================
            MESSAGES
        ================================================= */}

        <div className="chat-messages">

          {/* =================================================
              EMPTY STATE
          ================================================= */}

          {messages.length === 0 &&
            !loading && (

              <div className="chat-empty">

                <div className="empty-avatar">
                  <span>
                    KB
                  </span>
                </div>

                <div className="empty-badge">

                  <span className="badge-dot" />

                  Personal knowledge
                  assistant

                </div>

                <h2>
                  What would you like to
                  <span> know?</span>
                </h2>

                <p>
                  Ask a question about your
                  uploaded PDFs, notes, and
                  documents. Gemini will generate
                  one answer using the most
                  relevant sources.
                </p>

                <div className="suggestion-grid">

                  {suggestions.map(
                    (suggestion) => (

                      <button
                        key={suggestion}
                        type="button"
                        onClick={() =>
                          useSuggestion(
                            suggestion
                          )
                        }
                        className="suggestion-card"
                      >
                        {suggestion}
                      </button>

                    )
                  )}

                </div>

              </div>

            )}

          {/* =================================================
              CONVERSATION
          ================================================= */}

          {messages.map(
            (message) => {

              const isAssistant =
                message.role ===
                "assistant";

              const results =
                message.results ?? [];

              const hasSources =
                isAssistant &&
                results.length > 0;

              const sourcesExpanded =
                expandedSources[
                  message.id
                ] ?? true;

              return (
                <article
                  key={message.id}
                  className={`message-row ${
                    isAssistant
                      ? "assistant-row"
                      : "user-row"
                  }`}
                >

                  {/* =================================================
                      ASSISTANT AVATAR
                  ================================================= */}

                  {isAssistant && (
                    <div className="message-avatar">
                      KB
                    </div>
                  )}

                  <div
                    className={`message-content ${
                      isAssistant
                        ? "assistant-message"
                        : "user-message"
                    }`}
                  >

                    {/* =================================================
                        META
                    ================================================= */}

                    <div className="message-meta">

                      <div className="message-author">

                        <span>
                          {isAssistant
                            ? "Personal KB"
                            : "You"}
                        </span>

                        <time>
                          {formatTime(
                            message.timestamp
                          )}
                        </time>

                      </div>

                    </div>

                    {/* =================================================
                        ANSWER
                    ================================================= */}

                    <div className="message-bubble answer-bubble">

                      {message.content}

                    </div>

                    {/* =================================================
                        SOURCES
                    ================================================= */}

                    {hasSources && (

                      <div className="sources-container">

                        <button
                          type="button"
                          className="sources-toggle"
                          onClick={() =>
                            toggleSources(
                              message.id
                            )
                          }
                          aria-expanded={
                            sourcesExpanded
                          }
                        >

                          <span className="sources-toggle-left">

                            <span className="source-icon">
                              ◈
                            </span>

                            <span>
                              View{" "}
                              {
                                results.length
                              }{" "}
                              {results.length ===
                              1
                                ? "source"
                                : "sources"}
                            </span>

                          </span>

                          <svg
                            className={`source-chevron ${
                              sourcesExpanded
                                ? "expanded"
                                : ""
                            }`}
                            width="16"
                            height="16"
                            viewBox="0 0 24 24"
                            fill="none"
                            aria-hidden="true"
                          >
                            <path
                              d="M6 9l6 6 6-6"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>

                        </button>

                        {sourcesExpanded && (

                          <div className="sources-list">

                            {results.map(
                              (
                                result,
                                index
                              ) => {

                                const rawScore =
                                  Number(
                                    result.score
                                  );

                                const score =
                                  Number.isFinite(
                                    rawScore
                                  )
                                    ? Math.max(
                                        0,
                                        Math.min(
                                          1,
                                          rawScore
                                        )
                                      )
                                    : 0;

                                const percentage =
                                  score *
                                  100;

                                return (

                                  <article
                                    key={`${result.document_id}-${result.chunk_index}-${index}`}
                                    className="source-card"
                                  >

                                    {/* SOURCE HEADER */}

                                    <div className="source-header">

                                      <div className="source-index">
                                        {String(
                                          index +
                                            1
                                        ).padStart(
                                          2,
                                          "0"
                                        )}
                                      </div>

                                      <div className="source-info">

                                        <span className="source-label">
                                          SOURCE{" "}
                                          {index +
                                            1}
                                        </span>

                                        <h3>
                                          {
                                            result.document_name
                                          }
                                        </h3>

                                      </div>

                                      <div
                                        className={`source-score ${getScoreClass(
                                          score
                                        )}`}
                                      >

                                        <strong>
                                          {percentage.toFixed(
                                            0
                                          )}
                                          %
                                        </strong>

                                        <span>
                                          {getScoreLabel(
                                            score
                                          )}
                                        </span>

                                      </div>

                                    </div>

                                    {/* SCORE BAR */}

                                    <div className="source-score-track">

                                      <span
                                        style={{
                                          width: `${percentage}%`,
                                        }}
                                      />

                                    </div>

                                    {/* SOURCE META */}

                                    <div className="source-meta">

                                      <span>

                                        <svg
                                          width="13"
                                          height="13"
                                          viewBox="0 0 24 24"
                                          fill="none"
                                          aria-hidden="true"
                                        >
                                          <path
                                            d="M6 2h9l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Z"
                                            stroke="currentColor"
                                            strokeWidth="2"
                                          />

                                          <path
                                            d="M14 2v6h6"
                                            stroke="currentColor"
                                            strokeWidth="2"
                                          />
                                        </svg>

                                        {result.source ||
                                          result.document_name}

                                      </span>

                                      <span>
                                        Page{" "}
                                        {result.page_number ??
                                          "N/A"}
                                      </span>

                                      <span>
                                        Chunk{" "}
                                        {
                                          result.chunk_index
                                        }
                                      </span>

                                    </div>

                                    {/* SOURCE TEXT */}

                                    <p className="source-text">
                                      {
                                        result.text
                                      }
                                    </p>

                                  </article>

                                );
                              }
                            )}

                          </div>

                        )}

                      </div>

                    )}

                    {/* =================================================
                        NO SOURCES
                    ================================================= */}

                    {isAssistant &&
                      !hasSources && (

                        <div className="no-results">

                          <span className="no-results-icon">
                            !
                          </span>

                          <div>

                            <strong>
                              No relevant
                              information found
                            </strong>

                            <p>
                              Gemini could not find
                              enough relevant
                              information in your
                              uploaded documents.
                            </p>

                          </div>

                        </div>

                      )}

                  </div>

                </article>
              );
            }
          )}

          {/* =================================================
              LOADING
          ================================================= */}

          {loading && (

            <div className="message-row assistant-row">

              <div className="message-avatar">
                KB
              </div>

              <div className="message-content assistant-message">

                <div className="message-meta">

                  <div className="message-author">

                    <span>
                      Personal KB
                    </span>

                  </div>

                </div>

                <div className="message-bubble thinking">

                  <div className="thinking-animation">
                    <span />
                    <span />
                    <span />
                  </div>

                  <span>
                    Searching your documents
                    and generating an answer...
                  </span>

                </div>

              </div>

            </div>

          )}

          {/* =================================================
              ERROR
          ================================================= */}

          {error && (

            <div className="chat-error">

              <div className="error-icon">
                !
              </div>

              <div className="error-content">

                <strong>
                  Search failed
                </strong>

                <p>
                  {error}
                </p>

                {lastQuery && (

                  <button
                    type="button"
                    className="retry-button"
                    onClick={() =>
                      executeSearch(
                        lastQuery
                      )
                    }
                    disabled={loading}
                  >
                    Try again
                  </button>

                )}

              </div>

              <button
                type="button"
                className="error-close"
                onClick={() =>
                  setError("")
                }
                aria-label="Close error"
              >
                ×
              </button>

            </div>

          )}

          <div
            ref={messagesEndRef}
          />

        </div>

        {/* =================================================
            INPUT
        ================================================= */}

        <div className="chat-input-area">

          <form
            onSubmit={handleSearch}
            className="chat-input-form"
          >

            <textarea
              ref={textareaRef}
              value={query}
              onChange={(event) =>
                handleQueryChange(
                  event.target.value
                )
              }
              placeholder="Ask something about your documents..."
              rows={1}
              disabled={loading}
              aria-label="Ask your knowledge base"
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey
                ) {
                  event.preventDefault();

                  if (
                    query.trim() &&
                    !loading
                  ) {
                    handleSearch();
                  }
                }
              }}
            />

            {loading ? (

              <button
                type="button"
                onClick={stopSearch}
                className="send-button stop-button"
                aria-label="Stop search"
              >
                <span />
              </button>

            ) : (

              <button
                type="submit"
                disabled={
                  !query.trim()
                }
                className="send-button"
                aria-label="Send message"
              >

                <svg
                  width="19"
                  height="19"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M22 2L11 13"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />

                  <path
                    d="M22 2L15 22L11 13L2 9L22 2Z"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>

              </button>

            )}

          </form>

        </div>

      </section>

    </main>
  );
}