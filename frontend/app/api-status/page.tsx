"use client";
import { useEffect, useState } from "react";
import { api, HealthResponse } from "@/lib/api";

export default function ApiStatusPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .health()
      .then((h) => setHealth(h))
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-xl font-bold mb-4">API Status</h1>
        <p className="text-red-600">Error: {error}</p>
      </div>
    );
  }

  if (!health) {
    return (
      <div className="p-8">
        <h1 className="text-xl font-bold mb-4">API Status</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-xl font-bold mb-4">API Status</h1>
      <p className="mb-2">Status: {health.status}</p>
      <p>Timestamp: {new Date(health.timestamp).toLocaleString()}</p>
    </div>
  );
} 