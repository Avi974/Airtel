"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Clock,
  CheckCircle2,
  Calendar,
  Wrench,
  Wifi,
  Phone,
  MapPin,
  PlayCircle,
} from "lucide-react";
import { api, OrderTrackerResponse } from "@/lib/api";

const MILESTONE_ORDER = [
  "AWAITING_KYC_CONSENT",
  "READY_FOR_FULFILMENT",
  "SURVEY_SCHEDULED",
  "INSTALL_IN_PROGRESS",
  "ACTIVE",
];

function TrackerContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const orderIdParam = searchParams.get("order_id");

  const [orderId, setOrderId] = useState<string | null>(null);
  const [tracker, setTracker] = useState<OrderTrackerResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [advancing, setAdvancing] = useState(false);

  useEffect(() => {
    const oid = orderIdParam || localStorage.getItem("udyam_order_id");
    if (oid) {
      setOrderId(oid);
      loadTracker(oid);
    }
  }, [orderIdParam]);

  const loadTracker = async (oid: string) => {
    try {
      setLoading(true);
      const data = await api.getOrderTracker(oid);
      setTracker(data);
    } catch (err: any) {
      console.error("Failed to load tracker:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdvanceMilestone = async (toMilestone: string) => {
    if (!orderId) return;
    try {
      setAdvancing(true);
      await api.advanceMilestone(orderId, toMilestone);
      await loadTracker(orderId);
    } catch (err: any) {
      alert(`Simulator error: ${err.message}`);
    } finally {
      setAdvancing(false);
    }
  };

  if (!orderId) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center space-y-3">
        <Clock className="w-10 h-10 text-slate-400 mx-auto" />
        <h2 className="text-base font-bold text-slate-800">No Order to Track</h2>
        <p className="text-xs text-slate-500">
          Complete KYC to generate your digital fulfillment tracker.
        </p>
        <button
          onClick={() => router.push("/kyc")}
          className="bg-red-600 hover:bg-red-700 text-white font-semibold text-xs px-4 py-2 rounded-lg"
        >
          Go to KYC Verification
        </button>
      </div>
    );
  }

  const currentStepIdx = MILESTONE_ORDER.indexOf(tracker?.status || "READY_FOR_FULFILMENT");

  return (
    <div className="space-y-6">
      {/* Header & SLA Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-red-100 text-red-700 uppercase tracking-wide">
              Module 4
            </span>
            <h1 className="text-lg sm:text-xl font-bold text-slate-900">
              Live Order Tracker & Fulfillment SLA
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Order ID: <code className="bg-slate-100 px-1 py-0.5 rounded font-mono text-[11px]">{orderId}</code>
          </p>
        </div>

        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-2.5 px-3 flex items-center gap-2.5">
          <Clock className="w-4 h-4 text-emerald-600 shrink-0" />
          <div className="text-right sm:text-left">
            <span className="text-[10px] uppercase font-bold text-emerald-800 block">Catalogue-Driven SLA</span>
            <span className="text-xs font-extrabold text-emerald-900">
              {tracker?.expected_sla_days || 2} Days Activation Window
            </span>
          </div>
        </div>
      </div>

      {/* Visual Stepper */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-4">
          Activation Milestone Progress
        </span>

        <div className="grid grid-cols-4 gap-2 relative">
          {[
            { label: "Partner Dispatched", key: "READY_FOR_FULFILMENT" },
            { label: "Survey Scheduled", key: "SURVEY_SCHEDULED" },
            { label: "Installation Live", key: "INSTALL_IN_PROGRESS" },
            { label: "Service Active", key: "ACTIVE" },
          ].map((st, idx) => {
            const stepOrderIdx = idx + 1; // offset because index 0 is AWAITING_KYC_CONSENT
            const isCompleted = currentStepIdx > stepOrderIdx;
            const isCurrent = currentStepIdx === stepOrderIdx;

            return (
              <div key={st.key} className="text-center space-y-1.5">
                <div
                  className={`w-8 h-8 rounded-full mx-auto flex items-center justify-center font-bold text-xs transition shadow-xs ${
                    isCompleted
                      ? "bg-emerald-600 text-white"
                      : isCurrent
                      ? "bg-red-600 text-white ring-4 ring-red-100"
                      : "bg-slate-100 text-slate-400"
                  }`}
                >
                  {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : idx + 1}
                </div>
                <span
                  className={`text-[11px] font-bold block ${
                    isCurrent ? "text-red-600" : isCompleted ? "text-emerald-700" : "text-slate-400"
                  }`}
                >
                  {st.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Assigned Local Partner Details */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm space-y-3">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
          Assigned Accel Local Channel Partner
        </span>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50 p-3.5 rounded-lg border border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-700 font-bold text-sm">
              VS
            </div>
            <div>
              <span className="text-sm font-bold text-slate-900 block">
                {tracker?.assigned_partner?.partner_name || "Vikram Sharma (Channel Lead)"}
              </span>
              <span className="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
                <MapPin className="w-3 h-3 text-slate-400" />
                {tracker?.assigned_partner?.hub_location || "Accel B2B Hub · South Mumbai"}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={`tel:${tracker?.assigned_partner?.phone || "+919820012345"}`}
              className="bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition"
            >
              <Phone className="w-3.5 h-3.5 text-emerald-600" />
              Direct Call Partner
            </a>
          </div>
        </div>
      </div>

      {/* Simulator Control Tray (For Hackathon Presentation) */}
      <div className="bg-gradient-to-r from-red-950 via-slate-900 to-black rounded-xl p-5 text-white shadow-lg space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <PlayCircle className="w-4 h-4 text-red-500" />
            <span className="text-xs font-bold uppercase tracking-wider text-red-400">
              Demo Milestone Advance Simulator
            </span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">Simulates 2–4 day physical fulfillment</span>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Advance the order through field engineering milestones without waiting days:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1">
          <button
            onClick={() => handleAdvanceMilestone("SURVEY_SCHEDULED")}
            disabled={advancing}
            className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-bold py-2 px-3 rounded-lg text-xs flex items-center justify-center gap-1.5 transition disabled:opacity-50"
          >
            <Calendar className="w-3.5 h-3.5 text-blue-400" />
            1. Survey Scheduled
          </button>
          <button
            onClick={() => handleAdvanceMilestone("INSTALL_IN_PROGRESS")}
            disabled={advancing}
            className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-bold py-2 px-3 rounded-lg text-xs flex items-center justify-center gap-1.5 transition disabled:opacity-50"
          >
            <Wrench className="w-3.5 h-3.5 text-amber-400" />
            2. Install In Progress
          </button>
          <button
            onClick={() => handleAdvanceMilestone("ACTIVE")}
            disabled={advancing}
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-3 rounded-lg text-xs flex items-center justify-center gap-1.5 shadow transition disabled:opacity-50"
          >
            <Wifi className="w-3.5 h-3.5 text-emerald-300" />
            3. Activate Service (Live!)
          </button>
        </div>
      </div>

      {/* Chronological Event History */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm space-y-3">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
          Auditable Event History (Zero Polling Side Effects)
        </span>

        <div className="space-y-3 border-l-2 border-slate-200 pl-4 ml-2">
          {tracker?.events?.map((evt) => (
            <div key={evt.event_id} className="relative space-y-1">
              <div className="absolute -left-[23px] top-1 w-3 h-3 rounded-full bg-red-600 ring-4 ring-white" />
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-900">{evt.customer_title}</span>
                <span className="text-[10px] text-slate-400 font-mono">
                  {new Date(evt.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>
              <p className="text-xs text-slate-600">{evt.customer_detail}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function TrackerPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs text-slate-400">Loading Order Tracker...</div>}>
      <TrackerContent />
    </Suspense>
  );
}
