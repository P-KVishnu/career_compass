"use client";
import { useState, useEffect } from "react";
import { Toaster } from "sonner";
import { CareerAssessment } from "./CareerAssessment";
import { SignInForm } from "./SignInForm";
import ResultPage from "./ResultPage";

export default function App() {
  const [user, setUser] = useState<any>(null);
  const [predictedCareer, setPredictedCareer] = useState<string | null>(null);

  // ✅ Restore user session if exists
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem("user");
      }
    }
  }, []);

  // ✅ Handle Sign Out cleanly (no full reload)
  const handleSignOut = () => {
    localStorage.removeItem("user");
    setUser(null);
    setPredictedCareer(null);
  };

  // ✅ When Career Assessment completes
  const handleComplete = (career: any) => {
    const careerName =
      typeof career === "string"
        ? career.trim()
        : typeof career === "object" && career?.career
        ? String(career.career).trim()
        : "Unknown";

    console.log("🎯 Predicted Career:", careerName);

    if (careerName && careerName !== "") {
      setPredictedCareer(careerName);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex flex-col items-center justify-center p-6">
      <Toaster position="top-center" richColors />

      {/* ✅ If no user signed in */}
      {!user ? (
        <SignInForm />
      ) : predictedCareer ? (
        // ✅ Show result page after assessment
        <ResultPage
          resultData={{ career: predictedCareer }}
          onRestart={() => setPredictedCareer(null)}
        />
      ) : (
        // ✅ Main assessment area
        <div className="w-full flex flex-col items-center">
          <div className="flex justify-between w-full max-w-4xl mb-6">
            <h1 className="text-3xl font-bold text-gray-800">
              Welcome, {user.name || "User"} 👋
            </h1>
            <button
              onClick={handleSignOut}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
            >
              Sign Out
            </button>
          </div>

          {/* ✅ Render assessment */}
          <CareerAssessment onComplete={handleComplete} />
        </div>
      )}
    </div>
  );
}
