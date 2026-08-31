"use client";

import { useEffect, useId, useRef } from "react";
import { AlertTriangle, X } from "lucide-react";

type ConfirmDialogProps = {
  open: boolean;
  title: string;
  description: string;
  confirmLabel: string;
  busyLabel?: string;
  busy?: boolean;
  error?: string | null;
  destructive?: boolean;
  onCancel: () => void;
  onConfirm: () => void;
};

export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel,
  busyLabel = "Working...",
  busy = false,
  error,
  destructive = false,
  onCancel,
  onConfirm,
}: ConfirmDialogProps) {
  const titleId = useId();
  const descriptionId = useId();
  const cancelRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    cancelRef.current?.focus();
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && !busy) onCancel();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [busy, onCancel, open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#17120d]/45 p-5 backdrop-blur-[2px]">
      <section
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={descriptionId}
        className="paper-card record-shadow w-full max-w-md rounded-[8px] p-6"
      >
        <div className="flex items-start gap-4">
          <span className="rounded-full bg-[var(--danger)]/10 p-2 text-[var(--danger)]">
            <AlertTriangle size={19} aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <h2 id={titleId} className="text-xl font-semibold tracking-tight">{title}</h2>
            <p id={descriptionId} className="mt-2 text-sm leading-6 text-[var(--muted)]">{description}</p>
          </div>
          <button
            type="button"
            onClick={onCancel}
            disabled={busy}
            aria-label="Close confirmation"
            className="focus-ring rounded-[4px] p-1 text-[var(--muted)] disabled:opacity-40"
          >
            <X size={18} aria-hidden="true" />
          </button>
        </div>
        {error && (
          <p role="alert" className="mt-5 rounded-[6px] border border-[var(--danger)]/25 p-3 text-sm text-[var(--danger)]">
            {error}
          </p>
        )}
        <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            ref={cancelRef}
            type="button"
            onClick={onCancel}
            disabled={busy}
            className="tap focus-ring rounded-[6px] border border-[var(--rule)] px-4 py-2 text-sm font-medium disabled:opacity-40"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={busy}
            className={`tap focus-ring rounded-[6px] px-4 py-2 text-sm font-medium text-white disabled:cursor-wait disabled:opacity-55 ${
              destructive ? "bg-[var(--danger)]" : "bg-[var(--accent)]"
            }`}
          >
            {busy ? busyLabel : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}
