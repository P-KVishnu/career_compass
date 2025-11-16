import { useState } from "react";
import { toast } from "sonner";

interface CareerAssessmentProps {
  onComplete: (resultData?: any) => void;
}

export function CareerAssessment({ onComplete }: CareerAssessmentProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    personalityType: "",
    careerValues: [] as string[],
    currentRole: "",
    experienceLevel: "",
    educationLevel: "",
    preferredIndustries: [] as string[],
    technicalSkills: [] as Array<{ skill: string; level: number; yearsExperience: number }>,
    softSkills: [] as Array<{ skill: string; level: number }>,
    workStylePreferences: {
      remote: false,
      teamSize: "",
      workLifeBalance: 5,
      growthOriented: false,
    },
  });

  const personalityTypes = [
    "Analytical Thinker",
    "Creative Innovator",
    "People Leader",
    "Detail-Oriented Executor",
    "Strategic Visionary",
    "Collaborative Team Player",
    "Independent Problem Solver",
    "Empathetic Communicator",
  ];

  const careerValues = [
    "Work-Life Balance",
    "High Compensation",
    "Career Growth",
    "Job Security",
    "Creative Freedom",
    "Social Impact",
    "Leadership Opportunities",
    "Flexibility",
    "Learning & Development",
    "Recognition",
    "Autonomy",
    "Team Collaboration",
  ];

  const industries = [
    "Technology",
    "Healthcare",
    "Finance",
    "Education",
    "Marketing",
    "Consulting",
    "Manufacturing",
    "Retail",
    "Non-Profit",
    "Government",
    "Media & Entertainment",
    "Real Estate",
    "Transportation",
    "Energy",
  ];

  const commonTechnicalSkills = [
    "JavaScript",
    "Python",
    "Java",
    "React",
    "Node.js",
    "SQL",
    "AWS",
    "Data Analysis",
    "Machine Learning",
    "Project Management",
    "Digital Marketing",
    "Graphic Design",
    "Sales",
    "Customer Service",
    "Financial Analysis",
  ];

  const softSkills = [
    "Communication",
    "Leadership",
    "Problem Solving",
    "Teamwork",
    "Adaptability",
    "Time Management",
    "Critical Thinking",
    "Creativity",
    "Emotional Intelligence",
    "Negotiation",
    "Public Speaking",
    "Conflict Resolution",
  ];

  const handleSubmit = async () => {
    try {
      // ✅ Validate before sending
      if (!formData.personalityType || !formData.experienceLevel || !formData.educationLevel) {
        toast.error("Please complete all sections before submitting!");
        return;
      }
      const payload = {
  name: formData.currentRole?.trim() || "User",

  // 🔥 EXACT fields your backend expects:
  technicalSkills: formData.technicalSkills,  
  softSkills: formData.softSkills,

  industries: formData.preferredIndustries,  
  values: formData.careerValues,

  experience: formData.experienceLevel,
  education: formData.educationLevel,

  // Optional additional data (backend ignores them but safe to send)
  personality: formData.personalityType,
  workStyle: formData.workStylePreferences,
};



      console.log("🟢 Sending payload to backend:", payload);

      // ✅ Local backend fallback
const backendUrl =
  import.meta.env.VITE_API_URL ||
  "https://career-compass-bmzq.onrender.com";


     const response = await fetch(`${backendUrl}/api/predict`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    name,
    technicalSkills,
    softSkills,
    industries,
    values,
    experience,
    education,
  }),
});



      // ✅ Handle response
      if (!res.ok) {
        const errorText = await res.text();
        console.error("Backend responded with error:", errorText);
        toast.error(`Backend error: ${res.status}`);
        return;
      }

      const data = await res.json();
      console.log("✅ Received data:", data);

      if (data.error) {
        toast.error("Backend error: " + data.error);
        return;
      }

      toast.success("Career recommendations received!");

      // ✅ Send full response to next page
      onComplete(data);

    } catch (error) {
      console.error("❌ Failed to connect:", error);
      toast.error("Failed to connect to backend. Please check Flask server.");
    }
  };

  const steps = [
    {
      title: "Personality & Values",
      content: (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Which personality type best describes you?
            </label>
            <div className="grid grid-cols-2 gap-3">
              {personalityTypes.map((type) => (
                <button
                  key={type}
                  onClick={() => setFormData({ ...formData, personalityType: type })}
                  className={`p-3 text-left rounded-lg border transition-all ${
                    formData.personalityType === type
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              What do you value most in your career? (Select up to 4)
            </label>
            <div className="grid grid-cols-2 gap-3">
              {careerValues.map((value) => (
                <button
                  key={value}
                  onClick={() => {
                    const newValues = formData.careerValues.includes(value)
                      ? formData.careerValues.filter((v) => v !== value)
                      : formData.careerValues.length < 4
                      ? [...formData.careerValues, value]
                      : formData.careerValues;
                    setFormData({ ...formData, careerValues: newValues });
                  }}
                  className={`p-3 text-left rounded-lg border transition-all ${
                    formData.careerValues.includes(value)
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  {value}
                </button>
              ))}
            </div>
          </div>
        </div>
      ),
    },
    {
      title: "Background & Experience",
      content: (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Role (or most recent)
            </label>
            <input
              type="text"
              value={formData.currentRole}
              onChange={(e) => setFormData({ ...formData, currentRole: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Software Developer, Marketing Manager, Student"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Experience Level
            </label>
            <select
              value={formData.experienceLevel}
              onChange={(e) => setFormData({ ...formData, experienceLevel: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select experience level</option>
              <option value="entry">Entry Level (0-2 years)</option>
              <option value="mid">Mid Level (3-5 years)</option>
              <option value="senior">Senior Level (6-10 years)</option>
              <option value="executive">Executive Level (10+ years)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Education Level
            </label>
            <select
              value={formData.educationLevel}
              onChange={(e) => setFormData({ ...formData, educationLevel: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select education level</option>
              <option value="high-school">High School</option>
              <option value="associate">Associate Degree</option>
              <option value="bachelor">Bachelor's Degree</option>
              <option value="master">Master's Degree</option>
              <option value="phd">PhD/Doctorate</option>
              <option value="bootcamp">Bootcamp/Certification</option>
              <option value="self-taught">Self-Taught</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Preferred Industries (Select up to 3)
            </label>
            <div className="grid grid-cols-2 gap-3">
              {industries.map((industry) => (
                <button
                  key={industry}
                  onClick={() => {
                    const newIndustries = formData.preferredIndustries.includes(industry)
                      ? formData.preferredIndustries.filter((i) => i !== industry)
                      : formData.preferredIndustries.length < 3
                      ? [...formData.preferredIndustries, industry]
                      : formData.preferredIndustries;
                    setFormData({ ...formData, preferredIndustries: newIndustries });
                  }}
                  className={`p-3 text-left rounded-lg border transition-all ${
                    formData.preferredIndustries.includes(industry)
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  {industry}
                </button>
              ))}
            </div>
          </div>
        </div>
      ),
    },
    {
      title: "Skills Assessment",
      content: (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Technical Skills (Rate your proficiency 1-10)
            </label>
            <div className="space-y-3">
              {commonTechnicalSkills.map((skill) => {
                const existingSkill = formData.technicalSkills.find((s) => s.skill === skill);
                return (
                  <div key={skill} className="flex items-center gap-4">
                    <div className="flex-1">
                      <span className="text-sm">{skill}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={existingSkill?.level || 1}
                        onChange={(e) => {
                          const level = parseInt(e.target.value);
                          const newSkills = formData.technicalSkills.filter((s) => s.skill !== skill);
                          newSkills.push({
  skill,
  level,
  yearsExperience: existingSkill?.yearsExperience || 0
});

                          setFormData({ ...formData, technicalSkills: newSkills });
                        }}
                        className="w-20"
                      />
                      <span className="w-8 text-sm">{existingSkill?.level || 1}</span>
                                          </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Soft Skills (Rate your proficiency 1-10)
            </label>
            <div className="space-y-3">
              {softSkills.map((skill) => {
                const existingSkill = formData.softSkills.find((s) => s.skill === skill);
                return (
                  <div key={skill} className="flex items-center gap-4">
                    <div className="flex-1">
                      <span className="text-sm">{skill}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={existingSkill?.level || 1}
                        onChange={(e) => {
                          const level = parseInt(e.target.value);
                          const newSkills = formData.softSkills.filter((s) => s.skill !== skill);
                          newSkills.push({ skill, level });
                          setFormData({ ...formData, softSkills: newSkills });
                        }}
                        className="w-20"
                      />
                      <span className="w-8 text-sm">{existingSkill?.level || 1}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ),
    },
    {
      title: "Work Style Preferences",
      content: (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Remote Work Preference
            </label>
            <div className="flex gap-4">
              <button
                onClick={() =>
                  setFormData({
                    ...formData,
                    workStylePreferences: { ...formData.workStylePreferences, remote: true },
                  })
                }
                className={`px-4 py-2 rounded-lg border transition-all ${
                  formData.workStylePreferences.remote
                    ? "border-blue-500 bg-blue-50 text-blue-700"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                Prefer Remote/Hybrid
              </button>
              <button
                onClick={() =>
                  setFormData({
                    ...formData,
                    workStylePreferences: { ...formData.workStylePreferences, remote: false },
                  })
                }
                className={`px-4 py-2 rounded-lg border transition-all ${
                  !formData.workStylePreferences.remote
                    ? "border-blue-500 bg-blue-50 text-blue-700"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                Prefer In-Office
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preferred Team Size
            </label>
            <select
              value={formData.workStylePreferences.teamSize}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  workStylePreferences: { ...formData.workStylePreferences, teamSize: e.target.value },
                })
              }
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select team size preference</option>
              <option value="small">Small (2-5 people)</option>
              <option value="medium">Medium (6-15 people)</option>
              <option value="large">Large (16+ people)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Work-Life Balance Importance: {formData.workStylePreferences.workLifeBalance}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={formData.workStylePreferences.workLifeBalance}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  workStylePreferences: {
                    ...formData.workStylePreferences,
                    workLifeBalance: parseInt(e.target.value),
                  },
                })
              }
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Career Growth Orientation
            </label>
            <div className="flex gap-4">
              <button
                onClick={() =>
                  setFormData({
                    ...formData,
                    workStylePreferences: { ...formData.workStylePreferences, growthOriented: true },
                  })
                }
                className={`px-4 py-2 rounded-lg border transition-all ${
                  formData.workStylePreferences.growthOriented
                    ? "border-blue-500 bg-blue-50 text-blue-700"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                Growth-Focused
              </button>
              <button
                onClick={() =>
                  setFormData({
                    ...formData,
                    workStylePreferences: { ...formData.workStylePreferences, growthOriented: false },
                  })
                }
                className={`px-4 py-2 rounded-lg border transition-all ${
                  !formData.workStylePreferences.growthOriented
                    ? "border-blue-500 bg-blue-50 text-blue-700"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                Stability-Focused
              </button>
            </div>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-3xl font-bold text-gray-900">Career Assessment</h2>
          <span className="text-sm text-gray-500">
            Step {currentStep + 1} of {steps.length}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          ></div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg border p-8">
        <h3 className="text-2xl font-semibold text-gray-900 mb-6">
          {steps[currentStep].title}
        </h3>

        {steps[currentStep].content}

        <div className="flex justify-between mt-8">
          <button
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
            className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          {currentStep === steps.length - 1 ? (
            <button
              onClick={handleSubmit}
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all duration-200"
            >
              Complete Assessment
            </button>
          ) : (
            <button
              onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all duration-200"
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
