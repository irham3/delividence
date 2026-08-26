import { initializeApp, getApps } from "firebase/app";
import { GoogleAuthProvider, getAuth, signInWithPopup, signOut } from "firebase/auth";

// Config Firebase web app -- ini public config, bukan secret (02 §8 / 06 §6):
// aman di bundle client. Isolasi data sesungguhnya terjadi di backend lewat
// verifikasi ID token (app/auth.py), bukan lewat menyembunyikan config ini.
const firebaseConfig = {
  apiKey: "AIzaSyClurPoX2_8eOCAv4_cGglFwW3Zd9Dsw0M",
  authDomain: "dudepercobaan.firebaseapp.com",
  projectId: "dudepercobaan",
  storageBucket: "dudepercobaan.firebasestorage.app",
  messagingSenderId: "809536883160",
  appId: "1:809536883160:web:6d48fb0ecf49294375caad",
};

const app = getApps().length ? getApps()[0] : initializeApp(firebaseConfig);
export const auth = getAuth(app);

export function signInWithGoogle() {
  return signInWithPopup(auth, new GoogleAuthProvider());
}

export function signOutOwner() {
  return signOut(auth);
}
