import { useState, useEffect } from "react";

export function useCareerData() {
  const [userProfile, setUserProfile] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [roadmaps, setRoadmaps] = useState([]);
  const [simulations, setSimulations] = useState([]);

  // Mock load
  useEffect(() => {
    setUserProfile({
      _id: "1",
      personalityType: "INTJ",
      currentRole: "Software Engineer",
      experienceLevel: "Intermediate",
      educationLevel: "Bachelor’s",
      careerValues: ["Innovation", "Growth", "Autonomy"],
      preferredIndustries: ["Technology", "AI"],
      workStylePreferences: {
        remote: true,
        teamSize: "Medium",
        workLifeBalance: 7,
        growthOriented: true,
      },
      skillsAssessment: {
        technical: [
          { skill: "Python", level: 8, yearsExperience: 3 },
          { skill: "Machine Learning", level: 7, yearsExperience: 2 },
        ],
        soft: [
          { skill: "Communication", level: 8 },
          { skill: "Teamwork", level: 7 },
        ],
      },
    });
  }, []);

  const generateRecommendations = async () => {
    await new Promise((r) => setTimeout(r, 1500));
    setRecommendations({
      recommendations: [
        {
          title: "Data Scientist",
          industry: "Technology",
          fitScore: 89,
          salaryRange: { min: 80000, max: 130000 },
          growthPotential: 9,
          marketDemand: "high",
          reasoning: "Strong analytical and programming background.",
          requiredSkills: ["Python", "ML", "Data Analysis"],
          skillGaps: ["Deep Learning", "Statistics"],
          timeToTransition: "6 months",
        },
      ],
      marketAnalysis: {
        trendingSkills: ["AI", "Data Science", "Cloud"],
        decliningSkills: ["Manual QA", "Flash"],
      },
    });
  };

  const generateRoadmap = async (targetRole) => {
    await new Promise((r) => setTimeout(r, 1000));
    setRoadmaps((prev) => [
      ...prev,
      {
        _id: Date.now(),
        targetRole,
        currentSkillLevel: 5,
        targetSkillLevel: 8,
        totalEstimatedTime: "6 months",
        roadmap: [
          {
            phase: "Phase 1: Foundations",
            duration: "1 month",
            skills: ["Python", "Data Wrangling"],
            resources: [
              { title: "Python Basics", type: "Course", estimatedHours: 10, difficulty: "Easy", provider: "Coursera" },
            ],
            milestones: ["Complete Python course", "Build mini project"],
          },
        ],
      },
    ]);
  };

  const generateSimulation = async (scenarioName) => {
    await new Promise((r) => setTimeout(r, 1200));
    setSimulations((prev) => [
      ...prev,
      {
        _id: Date.now(),
        scenarioName,
        currentState: { role: "Software Engineer", salary: 90000, experience: 3, skills: ["Python", "ML"] },
        projectedPaths: [
          { year: 1, role: "Senior Engineer", salary: 110000, requiredActions: ["Upskill", "Certify"], probability: 0.8 },
          { year: 3, role: "Data Scientist", salary: 130000, requiredActions: ["Project experience"], probability: 0.6 },
        ],
        assumptions: ["Tech industry remains strong", "Continued AI growth"],
      },
    ]);
  };

  return {
    userProfile,
    recommendations,
    roadmaps,
    simulations,
    generateRecommendations,
    generateRoadmap,
    generateSimulation,
  };
}
