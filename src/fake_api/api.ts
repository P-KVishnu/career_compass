// src/fake_api/api.ts
export const api = {
  careers: {
    list: async () => {
      // Mock data — replace this later with real API or ML model output
      return [
        { id: 1, title: "Software Engineer", score: 92 },
        { id: 2, title: "Data Scientist", score: 88 },
        { id: 3, title: "AI Researcher", score: 85 },
      ];
    },
  },
  assessments: {
    save: async (answers: any) => {
      console.log("Mock saved assessment:", answers);
      return { status: "success" };
    },
  },
};
