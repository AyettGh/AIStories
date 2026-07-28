import "./globals.css";

export const metadata = {
  title: "Ayett Stories — Free AI Micro-Drama Studio",
  description:
    "A personalized, light Spotify-inspired micro-drama studio using Groq and free local media generation.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
