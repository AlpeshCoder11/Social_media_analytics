"use client";

import { TrendingUp } from "lucide-react";

const ACCENT = "#38BDF8";

export default function TrendsSection({ data }: { data: any[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-full min-h-[240px] flex-col overflow-hidden rounded-2xl border border-[#22304A] bg-[#121B2E]">
        <div className="h-1 w-full" style={{ backgroundColor: ACCENT }} />
        <div className="flex flex-1 flex-col p-5 sm:p-6">
          <div className="mb-4 flex items-center gap-2.5">
            <TrendingUp className="h-5 w-5" style={{ color: ACCENT }} />
            <h2 className="text-lg font-semibold text-[#EAF1FB]">Emerging Trends &amp; Velocity</h2>
          </div>
          <div className="flex flex-1 items-center justify-center text-center text-sm text-[#62789E]">
            Nothing trending in the current time window yet.
          </div>
        </div>
      </div>
    );
  }

  const getBadgeStyle = (type: string) => {
    switch (type) {
      case "emerging_viral":
        return "bg-[#2A1F3D] text-[#C084FC]";
      case "top_popular":
        return "bg-[#122A3D] text-[#38BDF8]";
      case "rising":
        return "bg-[#2E2410] text-[#FBBF24]";
      default:
        return "bg-[#1B2437] text-[#9FB1CC]";
    }
  };

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-2xl border border-[#22304A] bg-[#121B2E]">
      <div className="h-1 w-full" style={{ backgroundColor: ACCENT }} />
      <div className="flex flex-1 flex-col p-5 sm:p-6">
        <div className="mb-4 flex items-center gap-2.5">
          <TrendingUp className="h-5 w-5" style={{ color: ACCENT }} />
          <h2 className="text-lg font-semibold text-[#EAF1FB]">Emerging Trends &amp; Velocity</h2>
        </div>

        <div className="flex-1 overflow-x-auto">
          <table className="w-full min-w-[480px] border-collapse text-left">
            <thead>
              <tr className="border-b border-[#22304A] text-xs text-[#62789E]">
                <th className="pb-3 pr-3 font-medium">Topic</th>
                <th className="pb-3 pr-3 font-medium">Mentions</th>
                <th className="pb-3 pr-3 font-medium">Growth</th>
                <th className="pb-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.map((trend, idx) => (
                <tr
                  key={idx}
                  className="border-b border-[#1A2438] transition-colors last:border-0 hover:bg-[#16223A]"
                >
                  <td className="py-3 pr-3 text-sm font-medium capitalize text-[#EAF1FB]">
                    {trend.topic}
                  </td>
                  <td className="py-3 pr-3 text-sm text-[#9FB1CC]">{trend.current_volume}</td>
                  <td className="py-3 pr-3 text-sm font-semibold text-[#34D399]">
                    +{trend.growth_rate}%
                  </td>
                  <td className="py-3">
                    <span
                      className={`inline-block whitespace-nowrap rounded-full px-2.5 py-1 text-[11px] font-semibold ${getBadgeStyle(
                        trend.trend_type
                      )}`}
                    >
                      {trend.trend_type.replace("_", " ")}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}