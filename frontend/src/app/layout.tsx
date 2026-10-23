import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Inqolobane | Operations",
  description: "Read-only customer operations workbench.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
