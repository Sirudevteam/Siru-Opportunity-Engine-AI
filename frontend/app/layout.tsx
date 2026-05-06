import type { Metadata } from "next";
import { Raleway } from "next/font/google";
import "./globals.css";
import { AppShell } from "@/components/app-shell";

const raleway = Raleway({
  subsets: ["latin"],
  variable: "--font-raleway",
  display: "swap"
});

export const metadata: Metadata = {
  title: "Siru Opportunity Engine AI",
  description: "Internal lead intelligence and conversion engine for Siru."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={raleway.variable}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
