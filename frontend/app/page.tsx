"use client";

import { useAnalytics } from "../hooks/useAnalytics";
import SentimentSection from "../components/SentimentSection";
import TrendsSection from "../components/TrendsSection";
import DemographicsSection from "../components/DemographicsSection";
import NetworkSection from "../components/NetworkSection";

export default function Dashboard() {
  const { sentiment, trends, demographics, kols, bridges, loading, error, refresh } = useAnalytics();

  return (
    <main className="min-h-screen bg-[#0B1220] text-[#EAF1FB] antialiased">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-10 lg:py-10">
        {/* Header */}
        <header className="mb-8 flex flex-col gap-4 border-b border-[#22304A] pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs font-medium text-[#62789E]">
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  loading ? "bg-[#FBBF24] animate-pulse" : error ? "bg-[#F87171]" : "bg-[#34D399]"
                }`}
              />
              {loading ? "Syncing" : error ? "Connection issue" : "Live"}
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-[#EAF1FB] sm:text-3xl">
              Social Media Analytics
            </h1>
            <p className="mt-1 text-sm text-[#9FB1CC]">
              Audience intelligence, sentiment and network signal — updated in real time
            </p>
          </div>
          <button
            onClick={refresh}
            className="inline-flex items-center justify-center gap-2 self-start rounded-lg bg-[#22D3EE] px-4 py-2.5 text-sm font-semibold text-[#04222A] transition hover:bg-[#67E3F5] active:scale-[0.98] sm:self-auto"
          >
            Refresh data
          </button>
        </header>

        {/* Status Indicators */}
        {loading && (
          <div className="mb-6 rounded-lg border border-[#1E3A4C] bg-[#0F2530] px-4 py-3 text-sm text-[#7DD3E0]">
            Fetching the latest analytics from the FastAPI backend…
          </div>
        )}

        {error && (
          <div className="mb-6 rounded-lg border border-[#4C2626] bg-[#2A1414] px-4 py-3 text-sm text-[#F8B4B4]">
            Couldn&apos;t reach the backend: {error}
          </div>
        )}

        {/* Grid Container */}
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
          {/* Pillar 1: Sentiment Analysis */}
          <SentimentSection data={sentiment} />
          {/* Pillar 2: Demographics */}
          <DemographicsSection data={demographics} />
          {/* Pillar 3: Emerging Trends — full width, it's tabular */}
          <div className="lg:col-span-2">
            <TrendsSection data={trends} />
          </div>
          {/* Pillar 4: Link Analysis — full width, it's tabular */}
          <div className="lg:col-span-2">
            <NetworkSection kols={kols} bridges={bridges} />
          </div>
        </div>
      </div>
    </main>
  );
}