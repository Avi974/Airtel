"use client";

import React, { useState, useEffect, Suspense, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  CheckCircle,
  ShieldAlert,
  ArrowRight,
  Check,
} from "lucide-react";
import { api, PartnerQueueItem } from "@/lib/api";

function PartnerDeskContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const orderIdParam = searchParams.get("order_id");

  const [queue, setQueue] = useState<PartnerQueueItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterRole, setFilterRole] = useState<string>("");
  const [selectedOrder, setSelectedOrder] = useState<string | null>(orderIdParam || null);
  const [overrideReason, setOverrideReason] = useState("Physical premises and trade certificate inspected on-site by field partner.");
  const [overrideNotes, setOverrideNotes] = useState("Taxpayer status confirmed active via secondary state portal challan.");
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const loadQueue = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.getPartnerQueue(filterRole || undefined);
      setQueue(data);
    } catch (err: any) {
      console.error("Queue load error:", err);
    } finally {
      setLoading(false);
    }
  }, [filterRole]);

  useEffect(() => {
    loadQueue();
  }, [loadQueue]);

  const handleExecuteOverride = async () => {
    const oid = selectedOrder || queue[0]?.order_id;
    if (!oid) return;

    try {
      setLoading(true);
      const res = await api.overrideKyc(oid, overrideReason, overrideNotes);
      setActionSuccess(res.message);
      await loadQueue();
    } catch (err: any) {
      alert(`Override failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-900 text-white uppercase tracking-wide">
              Module 5 · Channel Ops
            </span>
            <h1 className="text-lg sm:text-xl font-bold text-slate-900">
              Partner Operations & Assisted KYC Desk
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Explainable Heuristic Priority Index (HPI) · Dual-Track Exception Escalation & On-Site Verification
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-semibold">
          <button
            onClick={() => setFilterRole("")}
            className={`px-3 py-1 rounded-md transition ${
              filterRole === "" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"
            }`}
          >
            All Items
          </button>
          <button
            onClick={() => setFilterRole("KYC_ASSISTANT")}
            className={`px-3 py-1 rounded-md transition ${
              filterRole === "KYC_ASSISTANT" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"
            }`}
          >
            KYC Exceptions
          </button>
          <button
            onClick={() => setFilterRole("LEAD_RECOVERY")}
            className={`px-3 py-1 rounded-md transition ${
              filterRole === "LEAD_RECOVERY" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"
            }`}
          >
            HPI Dropped Leads
          </button>
        </div>
      </div>

      {/* Success Notification */}
      {actionSuccess && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-emerald-900 flex items-center justify-between animate-in fade-in">
          <div className="flex items-center gap-2 text-xs sm:text-sm font-bold">
            <CheckCircle className="w-4 h-4 text-emerald-600" />
            {actionSuccess}
          </div>
          <button
            onClick={() => router.push(`/tracker?order_id=${selectedOrder || queue[0]?.order_id}`)}
            className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-1 shadow-sm transition"
          >
            View Live Tracker
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Main Grid: Queue on Left, Override Action Panel on Right */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left: Queue List */}
        <div className="md:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-3.5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Prioritized Dispatch Queue ({queue.length})
            </span>
            <span className="text-[10px] text-slate-400 font-mono">Ranked by HPI Score</span>
          </div>

          <div className="divide-y divide-slate-100 max-h-[460px] overflow-y-auto">
            {queue.map((item) => {
              const isSelected = selectedOrder === item.order_id;
              return (
                <div
                  key={item.item_id}
                  onClick={() => item.order_id && setSelectedOrder(item.order_id)}
                  className={`p-3.5 flex items-center justify-between gap-3 cursor-pointer transition ${
                    isSelected ? "bg-red-50/70 border-l-4 border-red-600" : "hover:bg-slate-50"
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs sm:text-sm text-slate-900">
                        {item.business_name || "Enterprise Lead"}
                      </span>
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                          item.role === "KYC_ASSISTANT"
                            ? "bg-amber-100 text-amber-800"
                            : "bg-blue-100 text-blue-800"
                        }`}
                      >
                        {item.role === "KYC_ASSISTANT" ? "KYC Review" : "Lead Recovery"}
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-500 flex items-center gap-2">
                      {item.contact_phone && <span>{item.contact_phone}</span>}
                      {item.flagged_reason && (
                        <>
                          <span>•</span>
                          <span className="text-rose-600 font-semibold">{item.flagged_reason}</span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* HPI Score Badge */}
                  <div className="text-right shrink-0">
                    <div className="flex items-center gap-1 justify-end">
                      <span className="text-xs text-slate-400 font-semibold">HPI:</span>
                      <span className="text-sm font-extrabold text-slate-900">
                        {item.priority_score}
                      </span>
                    </div>
                    <span className="text-[9px] text-slate-400 uppercase font-mono block">
                      {item.priority_score >= 80 ? "🔥 Hot" : "⚡ High"}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Assisted KYC Action Card */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm space-y-4">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-600" />
            <h2 className="text-sm font-bold text-slate-900">
              Assisted KYC: Verify & Override
            </h2>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed">
            Resolve planted defects (such as K01 Cancelled GSTIN or K11 Expired Document) by documenting field partner verification.
          </p>

          <div className="space-y-3 pt-1">
            <div>
              <label className="text-[11px] font-bold text-slate-700 uppercase block mb-1">
                Active Order Target
              </label>
              <input
                type="text"
                value={selectedOrder || queue[0]?.order_id || ""}
                onChange={(e) => setSelectedOrder(e.target.value)}
                placeholder="Order ID..."
                className="w-full bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-mono"
              />
            </div>

            <div>
              <label className="text-[11px] font-bold text-slate-700 uppercase block mb-1">
                Auditable Override Reason
              </label>
              <textarea
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                rows={2}
                className="w-full bg-white border border-slate-300 rounded-lg p-2 text-xs focus:ring-1 focus:ring-red-500"
              />
            </div>

            <div>
              <label className="text-[11px] font-bold text-slate-700 uppercase block mb-1">
                Field Evidence Notes
              </label>
              <textarea
                value={overrideNotes}
                onChange={(e) => setOverrideNotes(e.target.value)}
                rows={2}
                className="w-full bg-white border border-slate-300 rounded-lg p-2 text-xs focus:ring-1 focus:ring-red-500"
              />
            </div>

            <button
              onClick={handleExecuteOverride}
              disabled={loading}
              className="w-full bg-amber-600 hover:bg-amber-700 text-white font-bold py-2.5 px-4 rounded-lg text-xs flex items-center justify-center gap-1.5 shadow transition disabled:opacity-50"
            >
              <Check className="w-4 h-4" />
              Assisted KYC: Verify & Override
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function PartnerDeskPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs text-slate-400">Loading Partner Desk...</div>}>
      <PartnerDeskContent />
    </Suspense>
  );
}
