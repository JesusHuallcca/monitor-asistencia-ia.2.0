const API_BASE_URL = "http://127.0.0.1:8000";

async function apiRequest(path, options = {}) {
  const token = localStorage.getItem("asistencia_access_token");
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  let data = null;
  try {
    data = await response.json();
  } catch (_) {
    data = null;
  }

  if (!response.ok) {
    const message = data?.detail || data?.message || `Error HTTP ${response.status}`;
    throw new Error(message);
  }

  return data;
}
