import { useState } from "react";
import { toast } from "sonner";

interface CareerAssessmentProps {
  onComplete: (resultData?: any) => void;
}

// Backend URL
const backendUrl =
  import.meta.env.VITE_API_URL ||
  "https://career-compass-bmzq.onrender.com";

export function CareerAssessment({ onComplete }: CareerAssessmentProps) {
  const [currentStep, setCurrentStep] = useState(0);

  const [formData, setFormData] = useState({
    personalityType: "",
    careerValues: [] as string[],
    currentRole: "",
    experienceLevel: "",
    educationLevel: "",
    preferredIndustries: [] as string[],
    technicalSkills: [] as { skill: string; level: number }[],
    softSkills: [] as { skill: string; level: number }[],
    workStylePreferences: {
      remote: false,
      workLifeBalance: 5,
    },
  });

  const personalityOptions = [
    "Analytical Thinker",
    "Creative Innovator",
    "People Leader",
    "Detail-Oriented Executor",
    "Strategic Visionary",
  ];

  const skillOptions = ["Python", "JavaScript", "React", "SQL", "Java"];
  const softOptions = ["Communication", "Leadership", "Problem Solving"];
  const industryOptions = [
    "Technology",
    "Healthcare",
    "Finance",
    "Education",
  ];

  // --------------------------
  // 🔥 FIXED handleSubmit
  // --------------------------
  const handleSubmit = async () => {
    try {
      const payload = {
        name: formData.currentRole || "User",
        technicalSkills: formData.technicalSkills,
        softSkills: formData.softSkills,
        industries: formData.preferredIndustries,
        values: formData.careerValues,
        experience: formData.experienceLevel,
        education: formData.educationLevel,
      };

      const res = await fetch(`${backendUrl}/api/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        toast.error("Backend error");
        return;
      }

      const data = await res.json();
      onComplete(data);
      toast.success("Career recommendations received!");
    } catch (err) {
      toast.error("Backend connection failed");
      console.error(err);
    }
  };

  // --------------------------
  // All Steps
  // --------------------------
  const steps = [
    {
      title: "Personality",
      content: (
        <div className="space-y-4">
          {personalityOptions.map((p) => (
            <button
              key={p}
              onClick={() => setFormData({ ...formData, personalityType: p })}
              className={`p-3 border rounded-lg w-full ${
                formData.personalityType === p ? "bg-blue-100" : ""
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      ),
    },

    {
      title: "Experience",
      content: (
        <div className="space-y-4">
          <input
            type="text"
            className="w-full p-3 border rounded"
            placeholder="Current role"
            value={formData.currentRole}
            onChange={(e) =>
              setFormData({ ...formData, currentRole: e.target.value })
            }
          />

          <select
            className="w-full p-3 border rounded"
            value={formData.experienceLevel}
            onChange={(e) =>
              setFormData({ ...formData, experienceLevel: e.target.value })
            }
          >
            <option value="">Select experience</option>
            <option value="entry">Entry</option>
            <option value="mid">Mid</option>
            <option value="senior">Senior</option>
          </select>

          <select
            className="w-full p-3 border rounded"
            value={formData.educationLevel}
            onChange={(e) =>
              setFormData({ ...formData, educationLevel: e.target.value })
            }
          >
            <option value="">Select education</option>
            <option value="bachelor">Bachelor</option>
            <option value="master">Master</option>
            <option value="phd">PhD</option>
          </select>
        </div>
      ),
    },

    {
      title: "Technical Skills",
      content: (
        <div className="space-y-4">
          {skillOptions.map((skill) => {
            const found = formData.technicalSkills.find((s) => s.skill === skill);
            const level = found?.level || 1;

            return (
              <div key={skill} className="flex items-center gap-4">
                <span className="w-32">{skill}</span>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={level}
                  onChange={(e) => {
                    const newLevel = parseInt(e.target.value);
                    const updated = [
                      ...formData.technicalSkills.filter((s) => s.skill !== skill),
                      { skill, level: newLevel },
                    ];
                    setFormData({ ...formData, technicalSkills: updated });
                  }}
                />
                <span>{level}</span>
              </div>
            );
          })}
        </div>
      ),
    },

    {
      title: "Soft Skills",
      content: (
        <div className="space-y-4">
          {softOptions.map((skill) => {
            const found = formData.softSkills.find((s) => s.skill === skill);
            const level = found?.level || 1;

            return (
              <div key={skill} className="flex items-center gap-4">
                <span className="w-32">{skill}</span>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={level}
                  onChange={(e) => {
                    const newLevel = parseInt(e.target.value);
                    const updated = [
                      ...formData.softSkills.filter((s) => s.skill !== skill),
                      { skill, level: newLevel },
                    ];
                    setFormData({ ...formData, softSkills: updated });
                  }}
                />
                <span>{level}</span>
              </div>
            );
          })}
        </div>
      ),
    },

    {
      title: "Industries",
      content: (
        <div className="space-y-4">
          {industryOptions.map((ind) => (
            <button
              key={ind}
              onClick={() => {
                const exists = formData.preferredIndustries.includes(ind);
                const updated = exists
                  ? formData.preferredIndustries.filter((i) => i !== ind)
                  : [...formData.preferredIndustries, ind];

                setFormData({
                  ...formData,
                  preferredIndustries: updated,
                });
              }}
              className={`p-3 border rounded w-full ${
                formData.preferredIndustries.includes(ind)
                  ? "bg-blue-100"
                  : ""
              }`}
            >
              {ind}
            </button>
          ))}
        </div>
      ),
    },
  ];

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <h2 className="text-3xl font-bold mb-6">Career Assessment</h2>

      <div className="bg-white p-6 rounded-xl shadow">
        <h3 className="text-xl font-semibold mb-4">
          {steps[currentStep].title}
        </h3>

        {steps[currentStep].content}

        <div className="flex justify-between mt-8">
          <button
            disabled={currentStep === 0}
            onClick={() => setCurrentStep(currentStep - 1)}
            className="px-6 py-3 border rounded-lg disabled:opacity-40"
          >
            Previous
          </button>

          {currentStep === steps.length - 1 ? (
            <button
              onClick={handleSubmit}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg"
            >
              Complete Assessment
            </button>
          ) : (
            <button
              onClick={() => setCurrentStep(currentStep + 1)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg"
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
