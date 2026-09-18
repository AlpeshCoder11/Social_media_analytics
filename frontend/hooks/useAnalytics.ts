"use client";

import { useState, useEffect, useCallback } from "react";

const API_BASE = "http://localhost:8000/api";

export interface AnalyticsState {
  trends: any[];
  sentiment: any[];
  demographics: any[];
  kols: any[];
  bridges: any[];
  communities: any[];
  loading: boolean;
  error: string | null;
}

export function useAnalytics() {
  const [data, setData] = useState<AnalyticsState>({
    trends: [],
    sentiment: [],
    demographics: [],
    kols: [],
    bridges: [],
    communities: [],
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    try {
      const endpoints = [
        `${API_BASE}/trends/top`,
        `${API_BASE}/sentiment/distribution`,
        `${API_BASE}/demographics/summary`,
        `${API_BASE}/network/kols`,
        `${API_BASE}/network/bridges`,
        `${API_BASE}/network/communities`,
      ];

      const responses = await Promise.allSettled(
        endpoints.map((url) => fetch(url).then((res) => (res.ok ? res.json() : null)))
      );

      const [trends, sentiment, demo, kols, bridges, communities] = responses.map(
        (r) => (r.status === "fulfilled" ? r.value : null)
      );

      setData({
        trends: trends?.trends || [],
        sentiment: sentiment?.sentiment || [],
        demographics: demo?.demographics || [],
        kols: kols?.kols || [],
        bridges: bridges?.bridges || [],
        communities: communities?.communities || [],
        loading: false,
        error: null,
      });
    } catch (err: any) {
      setData((prev) => ({ ...prev, loading: false, error: err.message }));
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...data, refresh: fetchData };
}