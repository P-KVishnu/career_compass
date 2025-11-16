import React, { useEffect, useState } from "react";
import { toast } from "sonner";
import ChatAssistant from "./ChatAssistant";

interface Mentor {
  name: string;
  specialization?: string;
  experience?: string | number;
  contact?: string;
}

interface Job {
  title: string;
  company: string;
  location: string;
  salary: string;
  link: string;
}

interface ResultPageProps {
  resultData: any;
  onRestart: () => void;
}

const ResultPage: React.FC<ResultPageProps> = ({ resultData, onRestart }) => {
  const [roadmap, setRoadmap] = useState<string[]>([]);
  const [mentors, setMentors] = useState<Mentor[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  const backendUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const careerName = encodeURIComponent(resultData?.career || "");
        if (!careerName) return;

        // Fetch roadmap
        const roadmapRes = await fetch(`${backendUrl}/get_roadmap/${careerName}`);
        if (roadmapRes.ok) {
          const roadmapData = await roadmapRes.json();
          setRoadmap(roadmapData.roadmap || []);
        }

        // Fetch mentors
        const mentorsRes = await fetch(`${backendUrl}/get_mentors/${careerName}`);
        if (mentorsRes.ok) {
          const mentorsData = await mentorsRes.json();
          setMentors(mentorsData.mentors || []);
        }

        // ✅ Fetch live job listings from Flask API
        const jobsRes = await fetch(`${backendUrl}/api/jobs?career=${careerName}`);
        if (jobsRes.ok) {
          const jobsData = await jobsRes.json();
          setJobs(jobsData.jobs || []);
        }
      } catch (error) {
        console.error("❌ Backend fetch error:", error);
        toast.error("Could not fetch career details or job listings.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [resultData]);

  if (loading) {
    return (
      <div className="text-center py-20 text-gray-500">
        Loading your personalized career results...
      </div>
    );
  }

  // Build context data to send to ChatAssistant
  const contextData = {
    career: resultData?.career,
    recommendations: resultData?.recommendations || [],
    mentors,
    jobs,
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 bg-white shadow-lg rounded-2xl border">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
        🎯 Recommended Career: <span className="text-blue-600">{resultData?.career}</span>
      </h2>

      {/* Roadmap Section */}
      <div className="mb-10">
        <h3 className="text-2xl font-semibold mb-3 text-gray-800">📍 Career Roadmap</h3>
        {roadmap.length > 0 ? (
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            {roadmap.map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 italic">No roadmap available for this career yet.</p>
        )}
      </div>

      {/* Mentors Section */}
      <div className="mb-10">
        <h3 className="text-2xl font-semibold mb-4 text-gray-800">👩‍🏫 Recommended Mentors</h3>
        {mentors.length > 0 ? (
          <div className="grid md:grid-cols-2 gap-6">
            {mentors.map((mentor, idx) => (
              <div
                key={idx}
                className="p-5 border rounded-xl shadow-sm hover:shadow-md transition-all duration-200 bg-gray-50"
              >
                <h4 className="text-lg font-bold text-blue-700 mb-1">
                  {mentor.name || `Mentor ${idx + 1}`}
                </h4>
                <p className="text-sm text-gray-700">
                  <strong>Specialization:</strong> {mentor.specialization || "—"}
                </p>
                <p className="text-sm text-gray-700">
                  <strong>Experience:</strong>{" "}
                  {mentor.experience ? `${mentor.experience} years` : "—"}
                </p>
                <p className="text-sm text-gray-700">
                  <strong>Contact:</strong>{" "}
                  {mentor.contact && mentor.contact !== "—" ? mentor.contact : "—"}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 italic">No mentors found for this career.</p>
        )}
      </div>

      {/* ✅ Job Listings Section */}
      <div className="mb-10">
        <h3 className="text-2xl font-semibold mb-4 text-gray-800">💼 Latest Job Openings</h3>
        {jobs.length > 0 ? (
          <div className="space-y-4">
            {jobs.map((job, idx) => (
              <div
                key={idx}
                className="p-5 border rounded-xl shadow-sm hover:shadow-md transition-all duration-200 bg-gray-50"
              >
                <h4 className="text-lg font-bold text-blue-700">{job.title}</h4>
                <p className="text-sm text-gray-700">{job.company}</p>
                <p className="text-sm text-gray-600">
                  📍 {job.location} — 💰 {job.salary || "Not disclosed"}
                </p>
                <a
                  href={job.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 text-sm underline mt-1 inline-block"
                >
                  View Job →
                </a>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 italic">
            No live job data available for this role right now.
          </p>
        )}
      </div>

      {/* ✅ Integrated AI Chat Assistant */}
      <div className="mt-12">
        <h3 className="text-2xl font-semibold mb-4 text-gray-800 text-center">
          🤖 Chat with Your AI Career Assistant
        </h3>
        {/* 💬 Pass context data here */}
        <ChatAssistant resultData={contextData} />
      </div>

      {/* Restart Button */}
      <div className="text-center mt-10">
        <button
          onClick={onRestart}
          className="px-8 py-3 mt-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all duration-200"
        >
          🔁 Take Another Assessment
        </button>
      </div>
    </div>
  );
};

export default ResultPage;
