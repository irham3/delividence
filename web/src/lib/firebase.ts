import { initializeApp, getApps } from "firebase/app";
import { GoogleAuthProvider, getAuth, signInWithPopup, signOut, type Auth } from "firebase/auth";

// Firebase web config memang public (bukan secret), tetapi tetap harus milik
// project deployment ini. Jangan pernah mengirimkan staging project yang
// kebetulan dipakai saat development ke production (02 §8 / 06 §6).
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

let cachedAuth: Auth | null = null;

export function getFirebaseAuth() {
  if (cachedAuth) return cachedAuth;
  const missingConfig = Object.entries(firebaseConfig)
    .filter(([, value]) => !value)
    .map(([key]) => key);
  if (missingConfig.length > 0) {
    throw new Error(`Firebase is not configured: ${missingConfig.join(", ")}`);
  }
  const app = getApps().length ? getApps()[0] : initializeApp(firebaseConfig);
  cachedAuth = getAuth(app);
  return cachedAuth;
}

export function signInWithGoogle() {
  return signInWithPopup(getFirebaseAuth(), new GoogleAuthProvider());
}

export function signOutOwner() {
  return signOut(getFirebaseAuth());
}
