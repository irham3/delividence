"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { useRouter } from "next/navigation";
import { OwnerSignIn } from "@/components/delividence/owner-gate";
import { establishOwnerSession } from "@/lib/auth-flow";
import { getFirebaseAuth, signInWithGoogle } from "@/lib/firebase";
import { safeOwnerDestination } from "@/lib/route-policy";

export function AuthRoute({
  register = false,
  destination,
}: {
  register?: boolean;
  destination?: string;
}) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const synchronization = useRef<Promise<void> | null>(null);
  const safeDestination = safeOwnerDestination(destination);

  const synchronize = useCallback(
    (user: Parameters<typeof establishOwnerSession>[0]) => {
      if (!synchronization.current) {
        synchronization.current = establishOwnerSession(user)
          .then(() => router.replace(safeDestination))
          .catch((cause) => {
            synchronization.current = null;
            throw cause;
          });
      }
      return synchronization.current;
    },
    [router, safeDestination],
  );

  useEffect(() => {
    if (window.location.hostname === "127.0.0.1") {
      const canonical = new URL(window.location.href);
      canonical.hostname = "localhost";
      window.location.replace(canonical.toString());
      return;
    }

    let unsubscribe: () => void = () => {};
    let failureTimer: number | undefined = window.setTimeout(() => {
      setError(
        "Authentication took too long to initialize. Reload the page and use http://localhost:3000 when running locally.",
      );
      setCheckingSession(false);
    }, 8_000);
    try {
      unsubscribe = onAuthStateChanged(getFirebaseAuth(), (user) => {
        if (failureTimer) {
          window.clearTimeout(failureTimer);
          failureTimer = undefined;
        }
        if (user) {
          void synchronize(user).catch((cause) => {
            setError(cause instanceof Error ? cause.message : "Sign-in failed.");
            setCheckingSession(false);
          });
        } else {
          setCheckingSession(false);
        }
      });
    } catch (cause) {
      if (failureTimer) window.clearTimeout(failureTimer);
      failureTimer = window.setTimeout(() => {
        setError(cause instanceof Error ? cause.message : "Firebase is not configured.");
        setCheckingSession(false);
      }, 0);
    }
    return () => {
      unsubscribe();
      if (failureTimer) window.clearTimeout(failureTimer);
    };
  }, [synchronize]);

  async function handleSignIn() {
    setError(null);
    try {
      const credential = await signInWithGoogle();
      await synchronize(credential.user);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Sign-in failed.");
    }
  }

  if (checkingSession) {
    return (
      <main className="paper-texture flex min-h-[100dvh] items-center justify-center px-5">
        <p role="status" className="text-sm text-[var(--muted)]">Checking your session...</p>
      </main>
    );
  }

  return <OwnerSignIn register={register} error={error} onSignIn={handleSignIn} />;
}
