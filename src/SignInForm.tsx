"use client";
import { useState } from "react";
import { toast } from "sonner";

export function SignInForm() {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      toast.error("Please enter your name to continue.");
      return;
    }

    setLoading(true);
    setTimeout(() => {
      localStorage.setItem("user", JSON.stringify({ name }));
      toast.success(`Welcome, ${name}!`);
      setLoading(false);
      window.location.reload();
    }, 1000);
  };

  return (
    <form
      onSubmit={handleSignIn}
      className="bg-white p-8 rounded-xl shadow-lg border max-w-md w-full"
    >
      <h2 className="text-2xl font-bold text-center mb-6">
        Sign In to Career Compass
      </h2>

      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter your name"
        className="w-full px-4 py-3 mb-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-200"
      >
        {loading ? "Signing In..." : "Sign In"}
      </button>
    </form>
  );
}
