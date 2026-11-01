"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  FileText,
  Trash2,
  ArrowRight,
} from "lucide-react";
import { api, QuoteResponse } from "@/lib/api";

const ADDON_CATALOGUE = [
  { id: "P09", name: "Managed Wi-Fi Pro", category: "Value Added", price: 499 },
  { id: "P11", name: "Static IPv4 Address", category: "Addon", price: 300 },
  { id: "P10", name: "Cloud Firewall & Threat Defense", category: "Security", price: 799 },
  { id: "P07", name: "Biz Voice Unlimited (1 Line)", category: "Voice", price: 299 },
  { id: "P14", name: "Cloud Attendance & Workspace", category: "SaaS", price: 199 },
];

function QuoteContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const quoteIdParam = searchParams.get("quote_id");

  const [quoteId, setQuoteId] = useState<string | null>(null);
  const [quote, setQuote] = useState<QuoteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [contractMonths, setContractMonths] = useState(12);

  useEffect(() => {
    const qid = quoteIdParam || localStorage.getItem("udyam_quote_id");
    if (qid) {
      setQuoteId(qid);
      loadQuote(qid);
    }
  }, [quoteIdParam]);

  const loadQuote = async (qid: string) => {
    try {
      setLoading(true);
      const data = await api.getQuote(qid);
      setQuote(data);
      if (data.line_items.length > 0) {
        setContractMonths(data.line_items[0].contract_months);
      }
    } catch (err: any) {
      console.error("Failed to load quote:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleContractChange = async (months: number) => {
    if (!quoteId) return;
    setContractMonths(months);
    try {
      setLoading(true);
      const updated = await api.patchQuote(quoteId, [], [], months);
      setQuote(updated);
    } catch (err: any) {
      alert(`Could not update term: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAddon = async (productId: string, isCurrentlyIncluded: boolean) => {
    if (!quoteId) return;
    try {
      setLoading(true);
      const addIds = isCurrentlyIncluded ? [] : [productId];
      const removeIds = isCurrentlyIncluded ? [productId] : [];
      const updated = await api.patchQuote(quoteId, addIds, removeIds, contractMonths);
      setQuote(updated);
    } catch (err: any) {
      alert(`Failed to update addon: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptQuote = async () => {
    if (!quoteId) return;
    try {
      setLoading(true);
      const order = await api.acceptQuote(quoteId);
      localStorage.setItem("udyam_order_id", order.order_id);
      router.push(`/kyc?order_id=${order.order_id}`);
    } catch (err: any) {
      alert(`Failed to accept quote: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (!quote && !loading) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center space-y-3">
        <FileText className="w-10 h-10 text-slate-400 mx-auto" />
        <h2 className="text-base font-bold text-slate-800">No Active Quote Found</h2>
        <p className="text-xs text-slate-500">
          Please run discovery with the advisor to generate a commercial proposal.
        </p>
        <button
          onClick={() => router.push("/")}
          className="bg-red-600 hover:bg-red-700 text-white font-semibold text-xs px-4 py-2 rounded-lg"
        >
          Start Advisor Discovery
        </button>
      </div>
    );
  }

  const existingProductIds = new Set(quote?.line_items.map((i) => i.product_id) || []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-red-100 text-red-700 uppercase tracking-wide">
              Module 2
            </span>
            <h1 className="text-lg sm:text-xl font-bold text-slate-900">
              Commercial Quote & Tax Invoice
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Deterministic formula: <code className="bg-slate-100 px-1 py-0.5 rounded text-[11px]">v1.0-deterministic</code> · 100% Zero-hallucination arithmetic
          </p>
        </div>

        {/* Contract Term Selector */}
        <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-semibold">
          {[6, 12, 24, 36].map((m) => (
            <button
              key={m}
              onClick={() => handleContractChange(m)}
              className={`px-2.5 py-1 rounded-md transition ${
                contractMonths === m
                  ? "bg-red-600 text-white shadow-sm font-bold"
                  : "text-slate-600 hover:bg-white"
              }`}
            >
              {m}m {m >= 24 && "⭐"}
            </button>
          ))}
        </div>
      </div>

      {/* Line Items Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
            Selected Service Line Items
          </span>
          <span className="text-[11px] font-semibold text-slate-500">
            Place of Supply: State {quote?.line_items[0]?.site_state_code === "27" ? "27 (MH - Intra-State)" : "Inter-State (IGST 18%)"}
          </span>
        </div>

        <div className="divide-y divide-slate-100">
          {quote?.line_items.map((item) => (
            <div
              key={item.line_item_id}
              className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/60 transition"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-slate-900">{item.product_name}</span>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {item.category}
                  </span>
                  {item.serviceability_status === "SURVEY_REQUIRED" && (
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-100 text-amber-800">
                      Survey Required
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-slate-500 flex items-center gap-3">
                  <span>Site PIN: {item.site_pincode}</span>
                  <span>•</span>
                  <span>SLA: {item.sla_install_days} Days</span>
                  <span>•</span>
                  <span>Term: {item.contract_months} Months</span>
                </div>
              </div>

              {/* Price & GST breakdown */}
              <div className="flex items-center justify-between sm:justify-end gap-6 text-right">
                <div>
                  <span className="text-xs text-slate-400 block">Base Price</span>
                  <span className="font-bold text-slate-800 text-sm">
                    ₹{item.unit_monthly_inr.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block">
                    {item.site_state_code === "27" ? "CGST + SGST (18%)" : "IGST (18%)"}
                  </span>
                  <span className="font-semibold text-slate-600 text-xs">
                    +₹{(item.cgst_inr + item.sgst_inr + item.igst_inr).toLocaleString()}
                  </span>
                </div>
                <div className="min-w-[80px]">
                  <span className="text-xs text-slate-400 block">Total /mo</span>
                  <span className="font-extrabold text-red-600 text-sm">
                    ₹{item.total_monthly_inr.toLocaleString()}
                  </span>
                </div>

                {/* Remove button if optional addon */}
                {item.category !== "Connectivity" && (
                  <button
                    onClick={() => handleToggleAddon(item.product_id, true)}
                    className="text-slate-300 hover:text-red-600 p-1 transition"
                    title="Remove Addon"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Available Addons Tray */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-3">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-600 block">
          Available Enterprise Add-ons (Zero Prerequisite Deadlock)
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {ADDON_CATALOGUE.map((addon) => {
            const isAdded = existingProductIds.has(addon.id);
            return (
              <div
                key={addon.id}
                className={`p-3 rounded-lg border flex items-center justify-between transition ${
                  isAdded
                    ? "bg-slate-50 border-slate-300 text-slate-500"
                    : "bg-white border-slate-200 hover:border-red-200"
                }`}
              >
                <div>
                  <span className="font-bold text-xs text-slate-900 block">{addon.name}</span>
                  <span className="text-[10px] text-slate-500">₹{addon.price}/mo + GST</span>
                </div>
                <button
                  onClick={() => handleToggleAddon(addon.id, isAdded)}
                  disabled={loading}
                  className={`px-3 py-1.5 rounded-md text-xs font-bold flex items-center gap-1 transition ${
                    isAdded
                      ? "bg-red-50 text-red-600 border border-red-200 hover:bg-red-100"
                      : "bg-red-600 text-white hover:bg-red-700 shadow-sm"
                  }`}
                >
                  {isAdded ? "Remove" : "+ Add"}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Financial Summary & Order Lock Box */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-5 text-white shadow-lg space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-700 pb-4">
          <div>
            <span className="text-[10px] font-bold tracking-widest text-red-400 uppercase block">
              Quote Status: {quote?.status}
            </span>
            <span className="text-xl sm:text-2xl font-black text-white block mt-0.5">
              ₹{quote?.monthly_total_inr.toLocaleString()}{" "}
              <span className="text-xs font-normal text-slate-400">/ month inclusive of GST</span>
            </span>
            <span className="text-xs text-slate-400">
              One-time setup fee: ₹{quote?.one_time_total_inr.toLocaleString()} (waived on 12m+ terms)
            </span>
          </div>

          <button
            onClick={handleAcceptQuote}
            disabled={loading}
            className="w-full sm:w-auto bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-lg text-sm flex items-center justify-center gap-2 shadow transition disabled:opacity-50"
          >
            Accept Quote & Freeze Price
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* GST Invariant Proof */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-slate-300">
          <div>
            <span className="text-slate-500 block">Subtotal</span>
            <span className="font-semibold text-white">₹{quote?.monthly_subtotal_inr.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-slate-500 block">CGST (9%)</span>
            <span className="font-semibold text-white">₹{quote?.monthly_cgst_inr.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-slate-500 block">SGST (9%)</span>
            <span className="font-semibold text-white">₹{quote?.monthly_sgst_inr.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-slate-500 block">IGST (18%)</span>
            <span className="font-semibold text-white">₹{quote?.monthly_igst_inr.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function QuotePage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs text-slate-400">Loading Quote...</div>}>
      <QuoteContent />
    </Suspense>
  );
}
