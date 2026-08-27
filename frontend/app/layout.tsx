import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Personal Knowledge Base",
  description:
    "Personal Knowledge-Base MCP Server",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}