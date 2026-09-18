"use client";

import { Share2, GitMerge } from "lucide-react";

const ACCENT = "#C084FC";

export default function NetworkSection({ kols, bridges }: { kols: any[]; bridges: any[] }) {
  const hasKols = kols && kols.length > 0;
  const hasBridges = bridges && bridges.length > 0;

  if (!hasKols && !hasBridges) {
    return (
      <div className="flex h-full min-h-[240px] flex-col overflow-hidden rounded-2xl border border-[#22304A] bg-[#121B2E]">
        <div className="h-1 w-full" style={{ backgroundColor: ACCENT }} />
        <div className="flex flex-1 flex-col p-5 sm:p-6">
          <div className="mb-4 flex items-center gap-2.5">
            <Share2 className="h-5 w-5" style={{ color: ACCENT }} />
            <h2 className="text-lg font-semibold text-[#EAF1FB]">Network Intelligence</h2>
          </div>
          <div className="flex flex-1 items-center justify-center text-center text-sm text-[#62789E]">
            No network interaction data yet — bridge accounts and opinion leaders will appear here.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-2xl border border-[#22304A] bg-[#121B2E]">
      <div className="h-1 w-full" style={{ backgroundColor: ACCENT }} />
      <div className="flex flex-1 flex-col p-5 sm:p-6">
        <div className="mb-5 flex items-center gap-2.5">
          <Share2 className="h-5 w-5" style={{ color: ACCENT }} />
          <h2 className="text-lg font-semibold text-[#EAF1FB]">Network Intelligence</h2>
        </div>

        {/* Bridge Accounts (Betweenness Centrality) */}
        {hasBridges && (
          <div className="mb-6">
            <div className="mb-3 flex items-center gap-2">
              <GitMerge className="h-3.5 w-3.5 text-[#8FA1BF]" />
              <h3 className="text-xs font-medium text-[#8FA1BF]">Key connectors (bridges)</h3>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {bridges.slice(0, 3).map((bridge, idx) => (
                <div
                  key={idx}
                  className="rounded-lg border border-[#2E2447] bg-[#1A1530] p-3 text-center"
                >
                  <div className="truncate text-sm font-semibold text-[#D9B8FA]">
                    @{bridge.user_id}
                  </div>
                  <div className="mt-1 text-xs text-[#8B6FB0]">Cluster {bridge.community_id}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* KOL Leaderboard (PageRank) */}
        {hasKols && (
          <div className="flex-1">
            <h3 className="mb-3 text-xs font-medium text-[#8FA1BF]">Opinion leaders (authority)</h3>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[420px] border-collapse text-left">
                <thead>
                  <tr className="border-b border-[#22304A] text-xs text-[#62789E]">
                    <th className="pb-2 pr-3 font-medium">User</th>
                    <th className="pb-2 pr-3 font-medium">Authority score</th>
                    <th className="pb-2 text-right font-medium">Community</th>
                  </tr>
                </thead>
                <tbody>
                  {kols.slice(0, 5).map((kol, idx) => (
                    <tr
                      key={idx}
                      className="border-b border-[#1A2438] last:border-0 hover:bg-[#16223A]"
                    >
                      <td className="py-2.5 pr-3 text-sm font-medium text-[#EAF1FB]">
                        @{kol.user_id}
                      </td>
                      <td className="w-1/2 py-2.5 pr-3">
                        <div className="h-2 w-full rounded-full bg-[#1B2437]">
                          <div
                            className="h-2 rounded-full"
                            style={{
                              width: `${Math.min(kol.pagerank * 1500, 100)}%`,
                              backgroundColor: ACCENT,
                            }}
                          />
                        </div>
                      </td>
                      <td className="py-2.5 text-right text-xs font-medium text-[#62789E]">
                        C-{kol.community_id}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}