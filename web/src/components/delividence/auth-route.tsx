"use client";

import { useState } from "react";
import { OwnerSignIn } from "@/components/delividence/owner-gate";
import { signInWithGoogle } from "@/lib/firebase";

export function AuthRoute({ register = false }: { register?: boolean }) {
  const [error, setError] = useState<string | null>(null);
  return <OwnerSignIn register={register} error={error} onSignIn={() => signInWithGoogle().catch((cause) => setError(cause instanceof Error ? cause.message : "Sign-in failed."))} />;
}
