import "./globals.css";

export const metadata = {
  title: "SIH Social Media Analytics Dashboard",
  description: "Problem Statement 26152",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}