import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FactLens — Fact Knowledge Layer",
  description:
    "Extract, ground and reconcile facts across financial documents.",
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