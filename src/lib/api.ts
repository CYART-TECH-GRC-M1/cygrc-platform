import axios from "axios";

export const api = axios.create({
<<<<<<< HEAD
  baseURL: process.env.NEXT_PUBLIC_API_URL || "https://api.cygrc.com/v1",
=======
  baseURL: process.env.NEXT_PUBLIC_API_URL || "/api",
>>>>>>> origin/Abhishek
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("cygrc_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
