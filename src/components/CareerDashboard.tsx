import { useState, useEffect } from "react";
import { toast } from "sonner";

export function CareerDashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  // ✅ Fetch from Flask backend
  useEffect(() => {
    const fetchCareerData = async () => {
      try {
        const userName =
          JSON.parse(localStorage.getItem("user") || "{}")?.name || "User";

        const response = await fetch("http://127.0.0.1:5000/api/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: userName }),
        });

        if (!response.ok) throw new Error("Failed to fetch backend data");

        const result = await response.json();
        setData(result);
        setLoading(false);
      } catch (err) {
        console.error(err);
        toast.error(
          "Server error — please check backend! Failed to load career roadmap or mentor data."
        );
        setLoading(false);
      }
    };

    fetchCareerData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-20 text-gray-600">
        No data available — please check backend.
      </div>
    );
  }

  const { recommendations = [], mentors = [], roadmap = [] } = data;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Career Dashboard
        </h1>
        <p className="text-xl text-gray-600">
          Personalized roadmap, mentors, and recommendations for your career
          growth
        </p>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-8 bg-gray-100 p-1 rounded-xl">
        {[
          { id: "overview", label: "Overview", icon: "📊" },
          { id: "recommendations", label: "Careers", icon: "🎯" },
          { id: "mentors", label: "Mentors", icon: "🧑‍🏫" },
          { id: "roadmap", label: "Roadmap", icon: "🗺️" },
          { id: "preferences", label: "Preferences", icon: "⚙️" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${
              activeTab === tab.id
                ? "bg-white text-blue-600 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-lg border">
              <h3 className="text-lg font-semibold mb-2">👤 Welcome</h3>
              <p className="text-gray-600">
                Hi {data.user}! Here’s your personalized career summary powered
                by AI.
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-lg border">
              <h3 className="text-lg font-semibold mb-2">🎯 Career Options</h3>
              <p className="text-gray-600">
                {recommendations.length
                  ? `${recommendations.length} personalized suggestions`
                  : "No recommendations available."}
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-lg border">
              <h3 className="text-lg font-semibold mb-2">🧑‍🏫 Mentorship</h3>
              <p className="text-gray-600">
                {mentors.length
                  ? `${mentors.length} mentors found for your career path`
                  : "No mentors yet."}
              </p>
            </div>
          </div>
        )}

        {/* Recommendations Tab */}
        {activeTab === "recommendations" && (
          <div className="grid md:grid-cols-2 gap-6">
            {recommendations.map((rec: string, index: number) => (
              <div
                key={index}
                className="bg-white p-6 rounded-xl shadow-lg border hover:shadow-xl transition"
              >
                <h3 className="text-xl font-semibold text-blue-700">{rec}</h3>
                <p className="text-gray-600 mt-2">
                  A promising path that matches your interests and skills.
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Mentor Tab */}
        {activeTab === "mentors" && (
          <div className="grid md:grid-cols-2 gap-6">
            {mentors.map((mentor: string, index: number) => (
              <div
                key={index}
                className="bg-white p-6 rounded-xl shadow-lg border hover:shadow-xl transition"
              >
                <h3 className="text-lg font-semibold text-gray-900">
                  {mentor}
                </h3>
                <p className="text-gray-600">
                  Industry mentor ready to guide you in your chosen field.
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Roadmap Tab */}
        {activeTab === "roadmap" && (
          <div className="bg-white p-6 rounded-xl shadow-lg border">
            <h3 className="text-2xl font-semibold mb-4">🗺️ Career Roadmap</h3>
            <ol className="list-decimal list-inside space-y-3 text-gray-700">
              {roadmap.map((step: string, index: number) => (
                <li key={index} className="leading-relaxed">
                  {step}
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Preferences Tab */}
        {activeTab === "preferences" && (
          <div className="bg-white p-6 rounded-xl shadow-lg border">
            <h3 className="text-2xl font-semibold mb-4">
              ⚙️ Work Preferences
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block font-medium mb-1">
                  Work Type Preference:
                </label>
                <select
                  className="border border-gray-300 rounded-lg w-full p-2"
                  defaultValue="Work from Home"
                >
                  <option>Work from Home</option>
                  <option>In Office</option>
                  <option>Hybrid</option>
                </select>
              </div>

              <div>
                <label className="block font-medium mb-1">
                  Preferred Team Size:
                </label>
                <input
                  type="number"
                  className="border border-gray-300 rounded-lg w-full p-2"
                  placeholder="e.g. 5 to 10"
                />
              </div>

              <button
                onClick={() => toast.success("Preferences saved!")}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Save Preferences
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
