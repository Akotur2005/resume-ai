import { useState } from "react";
import ResumeBuilder from "./components/ResumeBuilder.jsx";
import ResumeReviewer from "./components/ResumeReviewer.jsx";
import JdResumeGenerator from "./components/JdResumeGenerator.jsx";

export default function App() {
  const [tab, setTab] = useState("builder");
  const [loadedResume, setLoadedResume] = useState(null);

  const handleEditInBuilder = (resumeConfig) => {
    setLoadedResume(resumeConfig);
    setTab("builder");
  };

  return (
    <div className="app">
      <header className="topbar no-print">
        <h1>Resume AI</h1>
        <nav>
          <button className={tab === "builder" ? "active" : ""} onClick={() => setTab("builder")}>
            Resume Builder
          </button>
          <button className={tab === "reviewer" ? "active" : ""} onClick={() => setTab("reviewer")}>
            ATS Reviewer
          </button>
          <button className={tab === "jd-to-resume" ? "active" : ""} onClick={() => setTab("jd-to-resume")}>
            Create by Job Description
          </button>
        </nav>
      </header>
      <main>
        {tab === "builder" && <ResumeBuilder initialResume={loadedResume} />}
        {tab === "reviewer" && <ResumeReviewer />}
        {tab === "jd-to-resume" && <JdResumeGenerator onEditInBuilder={handleEditInBuilder} />}
      </main>
    </div>
  );
}
