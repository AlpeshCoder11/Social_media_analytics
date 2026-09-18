"use client";

import { Users } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const ACCENT = "#FBBF24";

export default function DemographicsSection({ data }: { data: any[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-full min-h-[280px] flex-col overflow-hidden rounded-2xl border border-[#22304A] bg-[#121B2E]">
        <div className="h-1 w-full" style={{ backgroundColor: ACCENT }} />
        <div className="flex flex-1 flex-col p-5 sm:p-6">
          <div className="mb-4 flex items-center gap-2.5">
            <Users className="h-5 w-5" style={{ color: ACCENT }} />
            <h2 className="text-lg font-semibold text-[#EAF1FB]">Audience Professions</h2>
          </div>
          <div className="flex flex-1 items-center justify-center text-center text-sm text-[#62789E]">
            No aggregate demographic data yet — check back once the audience sample grows.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-[320px] flex-col overflow-hidden rounded-2xl border border-[#22304A] bg-[#121B2E]">
      <div className="h-1 w-full" style={{ backgroundColor: ACCENT }} />
      <div className="flex flex-1 flex-col p-5 sm:p-6">
        <div className="mb-1 flex items-center gap-2.5">
          <Users className="h-5 w-5" style={{ color: ACCENT }} />
          <h2 className="text-lg font-semibold text-[#EAF1FB]">Audience Professions</h2>
        </div>
        <p className="mb-4 text-xs text-[#62789E]">Anonymized segment counts</p>

        <div className="min-h-[220px] flex-1">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              layout="vertical"
              margin={{ top: 4, right: 24, left: 8, bottom: 0 }}
            >
              <XAxis type="number" hide />
              <YAxis
                dataKey="segment_name"
                type="category"
                axisLine={false}
                tickLine={false}
                width={110}
                tick={{ fill: "#9FB1CC", fontSize: 12, fontWeight: 500 }}
              />
              <Tooltip
                cursor={{ fill: "#16223A" }}
                contentStyle={{
                  borderRadius: "8px",
                  border: "1px solid #22304A",
                  background: "#0F1729",
                  color: "#EAF1FB",
                  fontSize: "13px",
                }}
                labelStyle={{ color: "#9FB1CC" }}
              />
              <Bar dataKey="total_users" radius={[0, 4, 4, 0]} barSize={20}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={ACCENT} fillOpacity={0.85} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}