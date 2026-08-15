"use client";

import {
  BrainCircuit,
  Database,
  FileSearch,
  Gauge,
} from "lucide-react";

export function Header() {
  return (
    <div className="mb-10 overflow-hidden rounded-2xl bg-gradient-to-r from-sky-600 via-blue-700 to-blue-900 px-6 py-8 text-white shadow-lg sm:px-8 sm:py-10">
      <div className="max-w-4xl">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-white/15 backdrop-blur">
            <BrainCircuit className="h-6 w-6" />
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
                AuthEvidence AI
              </h1>

              <span className="rounded-full border border-white/25 bg-white/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide">
                Healthcare AI
              </span>
            </div>

            <p className="mt-2 text-base font-medium text-white/95 sm:text-lg">
              Evidence-Grounded Prior Authorization Intelligence
            </p>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-white/80">
              FHIR-aware clinical evidence extraction, policy matching,
              confidence scoring, and documentation-gap detection for
              AI-assisted prior authorization review.
            </p>

            <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-xs font-medium text-white/85 sm:text-sm">
              <span className="flex items-center gap-1.5">
                <Database className="h-4 w-4" />
                FHIR Clinical Evidence
              </span>

              <span className="flex items-center gap-1.5">
                <FileSearch className="h-4 w-4" />
                Policy-Grounded Review
              </span>

              <span className="flex items-center gap-1.5">
                <Gauge className="h-4 w-4" />
                Readiness & Confidence Scoring
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}