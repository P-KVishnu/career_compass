// src/SignOutButton.tsx
"use client";
import { useState } from "react";

export function SignOutButton() {
  const [isSignedOut, setIsSignedOut] = useState(false);

  const handleSignOut = () => {
    localStorage.removeItem("user");
    setIsSignedOut(true);
    window.location.reload();
  };

  if (isSignedOut) return null;

  return (
    <button
      onClick={handleSignOut}
      className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:shadow-lg transition-all"
    >
      Sign Out
    </button>
  );
}
