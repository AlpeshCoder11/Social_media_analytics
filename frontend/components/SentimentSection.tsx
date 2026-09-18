"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { MessageCircle } from "lucide-react";

const ACCENT = "#34D399";

const EMOTION_COLORS: Record<string, string> = {
  positive: "#34D399",
  neutral: "#64748B",
  negative: "#F87171",
  excitement: "#FBBF24",
  anxiety: "#C084FC",
};

export default function SentimentSection({ data }: { data: any[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-full min-h-[280px] flex-col overflow-hidden rounded-2xl border border-[#22304A] bg-[#121B2E]">
        <div className="h-1 w-full" style={{ backgroundColor: ACCENT }} />
        <div className="flex flex-1 flex-col p-5 sm:p-6">
          <div className="mb-4 flex items-center gap-2.5">
            <MessageCircle className="h-5 w-5" style={{ color: ACCENT }} />
            <h2 className="text-lg font-semibold text-[#EAF1FB]">Sentiment Breakdown</h2>
          </div>
          <div className="flex flex-1 items-center justify-center text-center text-sm text-[#62789E]">
            No sentiment data yet — results appear once posts are classified.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-[320px] flex-col overflow-hidden rounded-2xl border border-[#22304A] bg-[#121B2E]">
      <div className="h-1 w-full" style={{ backgroundColor: ACCENT }} />
      <div className="flex flex-1 flex-col p-5 sm:p-6">
        <div className="mb-4 flex items-center gap-2.5">
          <MessageCircle className="h-5 w-5" style={{ color: ACCENT }} />
          <h2 className="text-lg font-semibold text-[#EAF1FB]">Sentiment Breakdown</h2>
        </div>

        <div className="min-h-[240px] flex-1">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="count"
                nameKey="emotion"
                cx="50%"
                cy="50%"
                innerRadius={68}
                outerRadius={98}
                paddingAngle={2}
                label={false}
              >
                {data.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={EMOTION_COLORS[entry.emotion.toLowerCase()] || "#38BDF8"}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  borderRadius: "8px",
                  border: "1px solid #22304A",
                  background: "#0F1729",
                  color: "#EAF1FB",
                  fontSize: "13px",
                }}
                itemStyle={{ color: "#EAF1FB", fontWeight: 500 }}
              />
              <Legend
                verticalAlign="bottom"
                height={36}
                iconType="circle"
                formatter={(value) => <span style={{ color: "#9FB1CC", fontSize: 12 }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}