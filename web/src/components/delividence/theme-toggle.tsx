"use client";

import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

const STORAGE_KEY = "delividence_theme";

export function ThemeToggle({ className = "" }: { className?: string }) {
  // Set for real in the layout.tsx init script before hydration; this just
  // mirrors it into React state so the icon can react to a click.
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    // Sync from the DOM attribute the layout.tsx init script already set,
    // once hydrated; rendering "light" first avoids an SSR/client mismatch.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setTheme(document.documentElement.dataset.theme === "dark" ? "dark" : "light");
  }, []);

  function toggle() {
    const next = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Private browsing / storage disabled -- toggle still works this load.
    }
    setTheme(next);
  }

  return (
    <button
      type="button"
      onClick={toggle}
      title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
      aria-label="Toggle color theme"
      className={`focus-ring tap surface-o60 inline-flex items-center justify-center rounded-[6px] border border-[var(--rule)] p-2 text-[var(--muted)] hover:text-[var(--ink)] ${className}`}
    >
      {theme === "dark" ? <Sun size={17} strokeWidth={1.8} /> : <Moon size={17} strokeWidth={1.8} />}
    </button>
  );
}
