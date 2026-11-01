"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Shield,
  AlertTriangle,
  Upload,
  CheckCircle,
  XCircle,
  RefreshCw,
  ArrowRight,
  Lock,
  Edit2,
  Check,
} from "lucide-react";
import { api, KycStatusResponse } from "@/lib/api";

const SPECIMENS = [
  { id: "K02", label: "K02 (Clean Path · Harmony Dental)", type: "clean" },
  { id: "K01", label: "K01 (Planted Defect · Cancelled GSTIN)", type: "defect" },
  { id: "K05", label: "K05 (Planted Defect · Missing Udyam)", type: "defect" },
  { id: "K11", label: "K11 (Planted Defect · Expired Bill >90d)", type: "defect" },
  { id: "K03", label: "K03 (Clean Path · Metro Diagnostics)", type: "clean" },
  { id: "K04", label: "K04 (Clean Path · Saffron Bakers)", type: "clean" },
];

function KycContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const orderIdParam = searchParams.get("order_id");

  const [orderId, setOrderId] = useState<string | null>(null);
  const [consentGranted, setConsentGranted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedSpecimen, setSelectedSpecimen] = useState("K02");
  const [kycReport, setKycReport] = useState<KycStatusResponse | null>(null);

  // Anti-substitution edit state
  const [editingField, setEditingField] = useState(false);
  const [editValue, setEditValue] = useState("");

  useEffect(() => {
    const oid = orderIdParam || localStorage.getItem("udyam_order_id");
    if (oid) {
      setOrderId(oid);
      loadKycStatus(oid);
    }
  }, [orderIdParam]);

  const loadKycStatus = async (oid: string) => {
    try {
      setLoading(true);
      const data = await api.getKycStatus(oid);
      setKycReport(data);
    } catch (err: any) {
      console.log("No existing KYC report:", err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGrantConsent = async () => {
    const sessId = localStorage.getItem("udyam_session_id");
    if (!sessId) return;
    try {
      setLoading(true);
      await api.grantConsent(sessId, "KYC_VERIFICATION");
      setConsentGranted(true);
    } catch (err: any) {
      alert(`Consent error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRunVerify = async (specimenId = selectedSpecimen) => {
    if (!orderId) return;
    try {
      setLoading(true);
      const res = await api.verifyKyc(orderId, specimenId);
      setKycReport(res);
      if (res.extracted_data?.gstin) {
        setEditValue(res.extracted_data.gstin);
      }
    } catch (err: any) {
      alert(`KYC verification error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAntiSubstitutionEdit = async () => {
    if (!orderId || !editValue) return;
    try {
      setLoading(true);
      const res = await api.editKycField(orderId, "gstin", editValue);
      setKycReport(res);
      setEditingField(false);
      alert("Anti-substitution check executed on your manual edit!");
    } catch (err: any) {
      alert(`Edit check failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (!orderId) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center space-y-3">
        <Shield className="w-10 h-10 text-slate-400 mx-auto" />
        <h2 className="text-base font-bold text-slate-800">No Active Order Selected</h2>
        <p className="text-xs text-slate-500">
          Accept a commercial quote first to begin digital KYC onboarding.
        </p>
        <button
          onClick={() => router.push("/quote")}
          className="bg-red-600 hover:bg-red-700 text-white font-semibold text-xs px-4 py-2 rounded-lg"
        >
          View Commercial Quote
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-red-100 text-red-700 uppercase tracking-wide">
              Module 3
            </span>
            <h1 className="text-lg sm:text-xl font-bold text-slate-900">
              Smart KYC & DPDP Consent Vault
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Order ID: <code className="bg-slate-100 px-1 py-0.5 rounded text-[11px] font-mono">{orderId.slice(0, 16)}...</code> · 3-Tier OCR with Anti-Substitution Gate
          </p>
        </div>

        {/* Specimen Switcher for Demo */}
        <div className="flex items-center gap-2 bg-slate-50 p-1.5 rounded-lg border border-slate-200">
          <span className="text-[10px] uppercase font-bold text-slate-500">Demo Specimen:</span>
          <select
            value={selectedSpecimen}
            onChange={(e) => {
              setSelectedSpecimen(e.target.value);
              handleRunVerify(e.target.value);
            }}
            className="text-xs font-semibold bg-white border border-slate-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-red-500"
          >
            {SPECIMENS.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* DPDP Act 2023 Consent Notice Box */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-3">
        <div className="flex items-start gap-3">
          <Lock className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h2 className="text-xs sm:text-sm font-bold text-slate-900">
              Purpose-Bound DPDP Consent (Digital Personal Data Protection Act 2023)
            </h2>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Accel Telecom processes your business registration documents solely for statutory B2B telecom service provisioning and GST input tax credit reconciliation. Documents are encrypted and automatically expunged post statutory KYC verification.
            </p>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
          <label className="flex items-center gap-2 text-xs font-semibold text-slate-700 cursor-pointer">
            <input
              type="checkbox"
              checked={consentGranted}
              onChange={handleGrantConsent}
              className="w-4 h-4 text-red-600 rounded border-slate-300 focus:ring-red-500"
            />
            <span>I grant consent for digital KYC extraction & verification</span>
          </label>
          <span className="text-[10px] text-slate-400 font-mono">Scope: KYC_VERIFICATION</span>
        </div>
      </div>

      {/* Document Slot Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        {[
          { label: "GST Certificate", key: "gst_certificate" },
          { label: "Udyam Certificate", key: "udyam_certificate" },
          { label: "Signatory ID", key: "signatory_id" },
          { label: "Address Proof (<90d)", key: "address_proof" },
        ].map((doc) => {
          const isUploaded = kycReport?.uploaded_docs?.includes(doc.key);
          const isMissingUdyam = selectedSpecimen === "K05" && doc.key === "udyam_certificate";
          return (
            <div
              key={doc.key}
              className={`p-3 rounded-lg border text-center space-y-1 transition ${
                isMissingUdyam
                  ? "bg-rose-50 border-rose-300 text-rose-800"
                  : isUploaded
                  ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                  : "bg-white border-slate-200 text-slate-600"
              }`}
            >
              <div className="flex justify-center">
                {isMissingUdyam ? (
                  <XCircle className="w-4 h-4 text-rose-600" />
                ) : isUploaded ? (
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                ) : (
                  <Upload className="w-4 h-4 text-slate-400" />
                )}
              </div>
              <span className="text-[11px] font-bold block truncate">{doc.label}</span>
              <span className="text-[10px] block opacity-80">
                {isMissingUdyam ? "Missing File" : isUploaded ? "Extracted" : "Pending"}
              </span>
            </div>
          );
        })}
      </div>

      {/* Verify Trigger Button */}
      <div className="flex gap-2">
        <button
          onClick={() => handleRunVerify(selectedSpecimen)}
          disabled={loading || !consentGranted}
          className="flex-1 bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 px-4 rounded-lg text-xs sm:text-sm flex items-center justify-center gap-2 shadow transition disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          Run Holistic 3-Tier KYC Verification ({selectedSpecimen})
        </button>
      </div>

      {/* Verification Results Panel */}
      {kycReport && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          {/* Decision Status Banner */}
          <div
            className={`p-4 rounded-xl border flex items-start gap-3 ${
              kycReport.decision === "PASS"
                ? "bg-emerald-50 border-emerald-200 text-emerald-900"
                : "bg-amber-50 border-amber-200 text-amber-900"
            }`}
          >
            {kycReport.decision === "PASS" ? (
              <CheckCircle className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="text-sm font-extrabold tracking-wide uppercase">
                  KYC Decision: {kycReport.decision}
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-white/80 shadow-xs">
                  Resolution: {kycReport.resolution_path}
                </span>
              </div>
              <p className="text-xs mt-1 leading-relaxed">
                {kycReport.decision === "PASS"
                  ? "All statutory checks validated cleanly. Order is auto-provisioned to READY_FOR_FULFILMENT."
                  : "Defect or exception identified. Escalated to Partner Ops Queue where an agent can perform Assisted KYC Override."}
              </p>
            </div>
          </div>

          {/* Itemized Checks */}
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
              Automated Check Results:
            </span>
            <div className="space-y-1.5">
              {kycReport.checks.map((chk, i) => (
                <div
                  key={i}
                  className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-2">
                    {chk.verdict === "MATCH" ? (
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    ) : (
                      <XCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                    )}
                    <div>
                      <span className="font-bold text-slate-800">{chk.check_code}</span>
                      <p className="text-[11px] text-slate-500">{chk.detail}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                        chk.verdict === "MATCH"
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-rose-100 text-rose-800"
                      }`}
                    >
                      {chk.verdict}
                    </span>
                    {chk.reason_code && (
                      <span className="block text-[9px] text-slate-400 font-mono mt-0.5">
                        {chk.reason_code}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Anti-Substitution Interactive Trap */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                <Edit2 className="w-3.5 h-3.5 text-slate-500" />
                Anti-Substitution Corroboration Field (GSTIN)
              </span>
              <span className="text-[10px] text-slate-400">Edits validate against raw OCR text</span>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                placeholder="Edit GSTIN to test Anti-Substitution check..."
                className="flex-1 bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-red-500"
              />
              <button
                onClick={handleAntiSubstitutionEdit}
                disabled={loading}
                className="bg-slate-900 hover:bg-black text-white text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-1 transition"
              >
                <Check className="w-3.5 h-3.5" />
                Test Edit
              </button>
            </div>
          </div>

          {/* Next Step Navigation */}
          <div className="pt-3 border-t border-slate-100 flex justify-end gap-2">
            {kycReport.decision === "PASS" ? (
              <button
                onClick={() => router.push(`/tracker?order_id=${orderId}`)}
                className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2.5 px-5 rounded-lg text-xs sm:text-sm flex items-center gap-1.5 shadow transition"
              >
                Track Live Order Fulfilment
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={() => router.push(`/partner?order_id=${orderId}`)}
                className="bg-amber-600 hover:bg-amber-700 text-white font-bold py-2.5 px-5 rounded-lg text-xs sm:text-sm flex items-center gap-1.5 shadow transition"
              >
                Open Partner Escalation Desk
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function KycPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs text-slate-400">Loading KYC Hub...</div>}>
      <KycContent />
    </Suspense>
  );
}
