// axios.js
// Make sure to include <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script> in HTML

// Create a global Axios instance
const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000/api/",
  timeout: 10000,
});

// Request interceptor: attach token if exists
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;
      if (status === 401 || status === 403) {
        console.warn("Unauthorized! Redirecting to login...");
        localStorage.removeItem("token");
      }
    }
    return Promise.reject(error);
  }
);

window.apiClient = apiClient;
