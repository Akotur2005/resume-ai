// All calls go to /api, which Vite proxies to the Express server (see vite.config.js).
async function request(url, options = {}) {
  const res = await fetch(url, options);
  if (res.status === 204) return null;
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.error || `Request failed (${res.status})`);
  return body;
}

const json = (method, body) => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const api = {
  listResumes: () => request("/api/resumes"),
  getResume: (id) => request(`/api/resumes/${id}`),
  createResume: (title, data) => request("/api/resumes", json("POST", { title, data })),
  updateResume: (id, title, data) => request(`/api/resumes/${id}`, json("PUT", { title, data })),
  deleteResume: (id) => request(`/api/resumes/${id}`, { method: "DELETE" }),

  improveBullet: (payload) => request("/api/resumes/ai/bullet", json("POST", payload)),
  generateSummary: (payload) => request("/api/resumes/ai/summary", json("POST", payload)),
  generateFromJd: (payload) => request("/api/resumes/ai/from-jd", json("POST", payload)),

  reviewBuilt: (data, jobDescription, resumeId) =>
    request("/api/reviews/builder", json("POST", { data, jobDescription, resumeId })),

  reviewUpload: (file, jobDescription) => {
    const form = new FormData();
    form.append("resume", file);
    form.append("jobDescription", jobDescription || "");
    return request("/api/reviews/upload", { method: "POST", body: form });
  },

  importPdf: (file) => {
    const form = new FormData();
    form.append("resume", file);
    return request("/api/reviews/import", { method: "POST", body: form });
  },

  listReviews: () => request("/api/reviews"),
  getReview: (id) => request(`/api/reviews/${id}`),
};
