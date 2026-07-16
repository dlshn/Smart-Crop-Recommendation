const API_BASE = "/api";

export async function fetchDistricts() {
  const res = await fetch(`${API_BASE}/districts`);
  if (!res.ok) throw new Error("Failed to fetch districts");
  return res.json();
}

export async function fetchCrops() {
  const res = await fetch(`${API_BASE}/crops`);
  if (!res.ok) throw new Error("Failed to fetch crops");
  return res.json();
}

export async function fetchRecommendations({ district, month, crops, lang = "en" }) {
  const res = await fetch(`${API_BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ district, month, crops, lang }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Failed to fetch recommendations");
  }
  return res.json();
}
