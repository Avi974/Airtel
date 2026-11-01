"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Send,
  Wifi,
  Radio,
  ArrowRight,
  Share2,
  Building2,
  Users,
  MapPin,
} from "lucide-react";
import { api, SessionData, BundleRecommendation } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  text: string;
}

export default function DiscoveryPage() {
  const router = useRouter();
  const [session, setSession] = useState<SessionData | null>(null);
  const [language, setLanguage] = useState<"en" | "hi" | "hinglish">("en");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [knownSlots, setKnownSlots] = useState<Record<string, any>>({});
  const [isReady, setIsReady] = useState(false);
  const [recommendation, setRecommendation] = useState<BundleRecommendation | null>(null);
  const [magicLink, setMagicLink] = useState<string | null>(null);

  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Initialize discovery session
  useEffect(() => {
    initSession(language);
  }, [language]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const initSession = async (lang: "en" | "hi" | "hinglish") => {
    try {
      setLoading(true);
      const sess = await api.createSession(lang);
      setSession(sess);
      localStorage.setItem("udyam_session_id", sess.session_id);

      // Initial welcoming greeting
      const greeting =
        lang === "hi"
          ? "नमस्ते! ऐक्सेल बिजनेस में आपका स्वागत है। आपके व्यवसाय के लिए हाई-स्पीड ब्रॉडबैंड और डिजिटल सॉल्यूशंस सिर्फ 15 मिनट में सक्रिय करें। आपके व्यवसाय का क्या प्रकार है?"
          : lang === "hinglish"
          ? "Namaste! Welcome to Accel Business. Apne shop ya office ke liye best broadband & voice plan select karein in 15 minutes. Aapka business kis category mein hai?"
          : "Welcome to Accel Telecom B2B! Power your enterprise with guaranteed broadband and unified digital services in one sitting. What type of business do you operate?";

      setMessages([{ role: "assistant", text: greeting }]);
      setKnownSlots({});
      setIsReady(false);
      setRecommendation(null);
    } catch (err) {
      console.error("Session init failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !session || loading) return;

    const userText = inputMessage.trim();
    setInputMessage("");
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setLoading(true);

    try {
      const res = await api.sendChatMessage(session.session_id, userText);
      setMessages((prev) => [...prev, { role: "assistant", text: res.reply }]);
      setKnownSlots(res.known_slots);

      if (res.is_ready_for_quote) {
        setIsReady(true);
        const rec = await api.getRecommendation(session.session_id);
        setRecommendation(rec);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Connection error. Please try sending again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateQuote = async () => {
    if (!session || !recommendation) return;
    try {
      setLoading(true);
      const productIds = [
        recommendation.primary_product.product_id,
        ...recommendation.included_addons.map((a) => a.product_id),
      ];
      const pincode = knownSlots.pincode || "400001";

      const quote = await api.createQuote({
        session_id: session.session_id,
        bundle_id: recommendation.bundle_id,
        product_ids: productIds,
        pincode: pincode,
        contract_months: 12,
      });

      localStorage.setItem("udyam_quote_id", quote.quote_id);
      router.push(`/quote?quote_id=${quote.quote_id}`);
    } catch (err: any) {
      alert(`Failed to create quote: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleMagicLink = async () => {
    if (!session) return;
    try {
      const res = await api.generateMagicLink(session.session_id, "whatsapp");
      setMagicLink(res.magic_url);
      navigator.clipboard?.writeText(res.magic_url);
      alert("Magic Link copied to clipboard! Share with your accountant or open on desktop to resume seamlessly.");
    } catch (err) {
      alert("Could not generate magic link.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero Header & Language Switcher */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-red-100 text-red-700 uppercase tracking-wide">
              Module 1
            </span>
            <h1 className="text-lg sm:text-xl font-bold text-slate-900">
              Conversational Digital Advisor
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Empathetic discovery & instant pincode serviceability mapping in real time.
          </p>
        </div>

        {/* Language selector */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-semibold">
          <button
            onClick={() => setLanguage("en")}
            className={`px-3 py-1 rounded-md transition ${
              language === "en" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"
            }`}
          >
            English
          </button>
          <button
            onClick={() => setLanguage("hi")}
            className={`px-3 py-1 rounded-md transition ${
              language === "hi" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"
            }`}
          >
            हिंदी
          </button>
          <button
            onClick={() => setLanguage("hinglish")}
            className={`px-3 py-1 rounded-md transition ${
              language === "hinglish" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"
            }`}
          >
            Hinglish
          </button>
        </div>
      </div>

      {/* Extracted Slots Indicator */}
      <div className="grid grid-cols-3 gap-2 sm:gap-3">
        <div
          className={`p-3 rounded-lg border text-left flex items-center gap-2.5 transition ${
            knownSlots.segment
              ? "bg-emerald-50 border-emerald-200 text-emerald-900"
              : "bg-white border-slate-200 text-slate-400"
          }`}
        >
          <Building2 className="w-4 h-4 shrink-0" />
          <div className="truncate">
            <span className="text-[10px] uppercase font-semibold block text-slate-500">Business</span>
            <span className="text-xs font-bold truncate block">
              {knownSlots.business_type || knownSlots.segment || "Pending..."}
            </span>
          </div>
        </div>

        <div
          className={`p-3 rounded-lg border text-left flex items-center gap-2.5 transition ${
            knownSlots.employee_count
              ? "bg-emerald-50 border-emerald-200 text-emerald-900"
              : "bg-white border-slate-200 text-slate-400"
          }`}
        >
          <Users className="w-4 h-4 shrink-0" />
          <div>
            <span className="text-[10px] uppercase font-semibold block text-slate-500">Team Size</span>
            <span className="text-xs font-bold block">
              {knownSlots.employee_count ? `${knownSlots.employee_count} Staff` : "Pending..."}
            </span>
          </div>
        </div>

        <div
          className={`p-3 rounded-lg border text-left flex items-center gap-2.5 transition ${
            knownSlots.pincode
              ? "bg-emerald-50 border-emerald-200 text-emerald-900"
              : "bg-white border-slate-200 text-slate-400"
          }`}
        >
          <MapPin className="w-4 h-4 shrink-0" />
          <div>
            <span className="text-[10px] uppercase font-semibold block text-slate-500">PIN Code</span>
            <span className="text-xs font-bold block">
              {knownSlots.pincode || "Pending..."}
            </span>
          </div>
        </div>
      </div>

      {/* Chat Thread */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col h-[380px]">
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-xs sm:text-sm leading-relaxed shadow-sm ${
                  m.role === "user"
                    ? "bg-red-600 text-white rounded-br-none"
                    : "bg-slate-100 text-slate-800 rounded-bl-none border border-slate-200"
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-100 rounded-2xl px-4 py-2 text-xs text-slate-500 animate-pulse">
                Advisor is typing...
              </div>
            </div>
          )}
          <div ref={chatBottomRef} />
        </div>

        {/* Input box */}
        <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-200 flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your reply (e.g. 'Dental clinic in 400001 with 8 staff')..."
            className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
          />
          <button
            type="submit"
            disabled={loading || !inputMessage.trim()}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-semibold text-xs sm:text-sm flex items-center gap-1.5 transition disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            Send
          </button>
        </form>
      </div>

      {/* Recommended Solution Card (Unlocks when slots are known) */}
      {recommendation && (
        <div className="bg-gradient-to-br from-red-50 via-white to-orange-50 rounded-xl border-2 border-red-200 p-5 shadow-md space-y-4 animate-in fade-in duration-300">
          <div className="flex items-start justify-between">
            <div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-600 text-white uppercase tracking-wider">
                Tailored Recommendation · {recommendation.suitability_score}% Match
              </span>
              <h2 className="text-base sm:text-lg font-bold text-slate-900 mt-1">
                {recommendation.title}
              </h2>
              <p className="text-xs text-slate-600">{recommendation.tagline}</p>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">Estimated Monthly</span>
              <span className="text-lg sm:text-xl font-extrabold text-red-600">
                ₹{recommendation.estimated_monthly_inr.toLocaleString()}
              </span>
              <span className="text-[10px] text-slate-400 block">+ 18% GST</span>
            </div>
          </div>

          {/* Upfront Feasibility Alert */}
          <div className="bg-white rounded-lg p-3 border border-orange-200 flex items-start gap-2.5 text-xs">
            {recommendation.primary_product.product_id === "P04" ? (
              <Radio className="w-4 h-4 text-orange-600 shrink-0 mt-0.5" />
            ) : (
              <Wifi className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            )}
            <div>
              <span className="font-bold text-slate-800 block">
                Infrastructure Check ({knownSlots.pincode}):
              </span>
              <p className="text-slate-600 mt-0.5">{recommendation.feasibility_notes}</p>
            </div>
          </div>

          {/* Included Products List */}
          <div className="space-y-1.5">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
              Package Inclusions:
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <div className="bg-white p-2.5 rounded-lg border border-slate-200 flex items-center justify-between">
                <div>
                  <span className="font-bold text-slate-800 block">
                    {recommendation.primary_product.name}
                  </span>
                  <span className="text-[10px] text-slate-500">
                    SLA: {recommendation.primary_product.sla_install_days} Days Activation
                  </span>
                </div>
                <span className="font-semibold text-slate-700">
                  ₹{recommendation.primary_product.unit_monthly_inr}/mo
                </span>
              </div>
              {recommendation.included_addons.map((add) => (
                <div
                  key={add.product_id}
                  className="bg-white p-2.5 rounded-lg border border-slate-200 flex items-center justify-between"
                >
                  <div>
                    <span className="font-bold text-slate-800 block">{add.name}</span>
                    <span className="text-[10px] text-slate-500">{add.category}</span>
                  </div>
                  <span className="font-semibold text-slate-700">₹{add.unit_monthly_inr}/mo</span>
                </div>
              ))}
            </div>
          </div>

          {/* Action CTAs */}
          <div className="pt-2 flex flex-col sm:flex-row gap-2.5">
            <button
              onClick={handleCreateQuote}
              disabled={loading}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 shadow-sm transition text-xs sm:text-sm"
            >
              Generate Commercial Quote & B2B GST
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={handleMagicLink}
              className="bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-1.5 text-xs sm:text-sm transition"
            >
              <Share2 className="w-3.5 h-3.5" />
              1-Tap CA Handoff
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
