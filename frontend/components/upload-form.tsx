"use client";

import { useState } from "react";
import { toast } from "sonner";
import {
  FileText,
  FlaskConical,
  Loader2,
  Send,
  User,
  Hash,
  Stethoscope,
  Activity,
} from "lucide-react";

import type { ReviewResponse } from "@/lib/types";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Alert,
  AlertDescription,
} from "@/components/ui/alert";


interface UploadFormProps {
  onReviewComplete: (review: ReviewResponse) => void;
}


interface AuthEvidenceForm {
  patient_id: string;
  age: string;
  gender: string;

  diagnosis_code: string;
  diagnosis_description: string;

  medication_name: string;
  medication_duration_weeks: string;

  treatment_description: string;

  encounter_reason: string;

  procedure_code: string;

  provider_npi: string;

  use_coverage_agent: boolean;
}


const emptyForm: AuthEvidenceForm = {
  patient_id: "",
  age: "",
  gender: "",

  diagnosis_code: "",
  diagnosis_description: "",

  medication_name: "",
  medication_duration_weeks: "",

  treatment_description: "",

  encounter_reason: "",

  procedure_code: "72148",

  provider_npi: "",

  use_coverage_agent: false,
};


const sampleForm: AuthEvidenceForm = {
  patient_id: "PAT-1002",
  age: "61",
  gender: "male",

  diagnosis_code: "M54.16",
  diagnosis_description: "Lumbar radiculopathy",

  medication_name: "Ibuprofen",
  medication_duration_weeks: "8",

  treatment_description: "Physical therapy",

  encounter_reason: "Persistent lower-back pain",

  procedure_code: "72148",

  provider_npi: "",

  use_coverage_agent: false,
};


export function UploadForm({
  onReviewComplete,
}: UploadFormProps) {
  const [form, setForm] = useState<AuthEvidenceForm>(emptyForm);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState<string | null>(null);


  function updateField<K extends keyof AuthEvidenceForm>(
    key: K,
    value: AuthEvidenceForm[K]
  ) {
    setForm((prev) => ({
      ...prev,
      [key]: value,
    }));
  }


  function loadSample() {
    setForm(sampleForm);
    setError(null);
  }


  async function handleSubmit(
    event: React.FormEvent
  ) {
    event.preventDefault();

    setError(null);

    if (!form.patient_id.trim()) {
      setError("Patient ID is required.");
      return;
    }

    if (!form.procedure_code.trim()) {
      setError("Procedure code is required.");
      return;
    }

    if (!form.diagnosis_description.trim()) {
      setError("Diagnosis description is required.");
      return;
    }

    setLoading(true);

    try {
      const conditions = [
        {
          code: form.diagnosis_code.trim(),
          description: form.diagnosis_description.trim(),
          status: "active",
        },
      ];

      const medications =
        form.medication_name.trim()
          ? [
              {
                name: form.medication_name.trim(),
                status: "completed",
                duration_weeks:
                  form.medication_duration_weeks
                    ? Number(form.medication_duration_weeks)
                    : null,
              },
            ]
          : [];

      const procedures =
        form.treatment_description.trim()
          ? [
              {
                code: "97110",
                description: form.treatment_description.trim(),
                date: new Date().toISOString().slice(0, 10),
              },
            ]
          : [];

      const encounters =
        form.encounter_reason.trim()
          ? [
              {
                type: "outpatient",
                reason: form.encounter_reason.trim(),
              },
            ]
          : [];

      const requestBody = {
        patient_data: {
          patient_id: form.patient_id.trim(),

          age: form.age
            ? Number(form.age)
            : null,

          gender: form.gender || null,

          conditions,

          medications,

          procedures,

          observations: [],

          encounters,
        },

        procedure_code: form.procedure_code.trim(),

        provider_npi:
          form.provider_npi.trim() || null,

        use_coverage_agent:
          form.use_coverage_agent,
      };

      console.log(
        "AuthEvidence request:\n" +
          JSON.stringify(requestBody, null, 2)
      );

      const response = await fetch(
        "http://127.0.0.1:8000/api/authevidence/review",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify(requestBody),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        const message =
          data?.detail ??
          "Prior authorization review failed.";

        throw new Error(
          typeof message === "string"
            ? message
            : JSON.stringify(message)
        );
      }

      onReviewComplete(data as ReviewResponse);

      const readiness =
        data.authorization_readiness?.readiness_score;

      toast.success(
        "AuthEvidence review complete",
        {
          description:
            readiness !== undefined
              ? `Authorization readiness: ${readiness}%`
              : "Review completed successfully.",
        }
      );
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Unable to complete review.";

      setError(message);

      toast.error(
        "Review failed",
        {
          description: message,
        }
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <Card className="shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between gap-4 pb-3">

        <div>
          <CardTitle className="text-lg flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            New Prior Authorization Review
          </CardTitle>

          <p className="text-sm text-muted-foreground mt-1">
            Submit clinical evidence for evidence-grounded policy review
          </p>
        </div>

        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={loadSample}
        >
          <FlaskConical className="mr-1 h-3.5 w-3.5" />
          Load Sample
        </Button>

      </CardHeader>


      <CardContent>

        <form
          onSubmit={handleSubmit}
          className="space-y-6"
        >

          {/* Patient */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>

            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">
                Patient
              </span>
            </div>
          </div>


          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">

            <div className="space-y-2">
              <Label
                htmlFor="patient_id"
                className="flex items-center gap-1.5"
              >
                <User className="h-3.5 w-3.5 text-muted-foreground" />
                Patient ID
              </Label>

              <Input
                id="patient_id"
                placeholder="PAT-1001"
                value={form.patient_id}
                onChange={(e) =>
                  updateField(
                    "patient_id",
                    e.target.value
                  )
                }
                required
              />
            </div>


            <div className="space-y-2">
              <Label htmlFor="age">
                Age
              </Label>

              <Input
                id="age"
                type="number"
                min="0"
                max="120"
                placeholder="58"
                value={form.age}
                onChange={(e) =>
                  updateField(
                    "age",
                    e.target.value
                  )
                }
              />
            </div>


            <div className="space-y-2">
              <Label htmlFor="gender">
                Gender
              </Label>

              <select
                id="gender"
                value={form.gender}
                onChange={(e) =>
                  updateField(
                    "gender",
                    e.target.value
                  )
                }
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs"
              >
                <option value="">
                  Select
                </option>

                <option value="female">
                  Female
                </option>

                <option value="male">
                  Male
                </option>

                <option value="other">
                  Other
                </option>

                <option value="unknown">
                  Unknown
                </option>
              </select>
            </div>

          </div>


          {/* Clinical evidence */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>

            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">
                Clinical Evidence
              </span>
            </div>
          </div>


          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">

            <div className="space-y-2">
              <Label
                htmlFor="diagnosis_code"
                className="flex items-center gap-1.5"
              >
                <Stethoscope className="h-3.5 w-3.5 text-muted-foreground" />
                Diagnosis Code
              </Label>

              <Input
                id="diagnosis_code"
                placeholder="M54.16"
                value={form.diagnosis_code}
                onChange={(e) =>
                  updateField(
                    "diagnosis_code",
                    e.target.value
                  )
                }
              />
            </div>


            <div className="space-y-2">
              <Label htmlFor="diagnosis_description">
                Diagnosis
              </Label>

              <Input
                id="diagnosis_description"
                placeholder="Lumbar radiculopathy"
                value={form.diagnosis_description}
                onChange={(e) =>
                  updateField(
                    "diagnosis_description",
                    e.target.value
                  )
                }
                required
              />
            </div>

          </div>


          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">

            <div className="space-y-2">
              <Label htmlFor="medication_name">
                Medication
              </Label>

              <Input
                id="medication_name"
                placeholder="Ibuprofen"
                value={form.medication_name}
                onChange={(e) =>
                  updateField(
                    "medication_name",
                    e.target.value
                  )
                }
              />
            </div>


            <div className="space-y-2">
              <Label htmlFor="medication_duration_weeks">
                Medication Duration (weeks)
              </Label>

              <Input
                id="medication_duration_weeks"
                type="number"
                min="0"
                placeholder="8"
                value={form.medication_duration_weeks}
                onChange={(e) =>
                  updateField(
                    "medication_duration_weeks",
                    e.target.value
                  )
                }
              />
            </div>

          </div>


          <div className="space-y-2">
            <Label htmlFor="treatment_description">
              Prior Treatment / Procedure
            </Label>

            <Input
              id="treatment_description"
              placeholder="Physical therapy"
              value={form.treatment_description}
              onChange={(e) =>
                updateField(
                  "treatment_description",
                  e.target.value
                )
              }
            />

            <p className="text-xs text-muted-foreground">
              Leave this empty to simulate missing conservative-treatment evidence.
            </p>
          </div>


          <div className="space-y-2">
            <Label
              htmlFor="encounter_reason"
              className="flex items-center gap-1.5"
            >
              <Activity className="h-3.5 w-3.5 text-muted-foreground" />
              Clinical / Encounter Reason
            </Label>

            <Textarea
              id="encounter_reason"
              rows={3}
              placeholder="Persistent lower-back pain"
              value={form.encounter_reason}
              onChange={(e) =>
                updateField(
                  "encounter_reason",
                  e.target.value
                )
              }
            />
          </div>


          {/* Authorization */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>

            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">
                Authorization
              </span>
            </div>
          </div>


          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">

            <div className="space-y-2">
              <Label
                htmlFor="procedure_code"
                className="flex items-center gap-1.5"
              >
                <Hash className="h-3.5 w-3.5 text-muted-foreground" />
                Requested Procedure Code
              </Label>

              <Input
                id="procedure_code"
                placeholder="72148"
                value={form.procedure_code}
                onChange={(e) =>
                  updateField(
                    "procedure_code",
                    e.target.value
                  )
                }
                required
              />

              <p className="text-xs text-muted-foreground">
                72148 = Lumbar MRI, 73721 = Knee MRI
              </p>
            </div>


            <div className="space-y-2">
              <Label htmlFor="provider_npi">
                Provider NPI (optional)
              </Label>

              <Input
                id="provider_npi"
                placeholder="1234567890"
                value={form.provider_npi}
                onChange={(e) =>
                  updateField(
                    "provider_npi",
                    e.target.value
                  )
                }
              />
            </div>

          </div>


          <label className="flex items-start gap-3 rounded-lg border p-3 cursor-pointer">

            <input
              type="checkbox"
              checked={form.use_coverage_agent}
              onChange={(e) =>
                updateField(
                  "use_coverage_agent",
                  e.target.checked
                )
              }
              className="mt-1"
            />

            <div>
              <p className="text-sm font-medium">
                Enable CMS/NPI Coverage Enrichment
              </p>

              <p className="text-xs text-muted-foreground">
                Uses the optional external Coverage Agent when available.
              </p>
            </div>

          </label>


          {error && (
            <Alert variant="destructive">
              <AlertDescription>
                {error}
              </AlertDescription>
            </Alert>
          )}


          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-brand to-brand-dark hover:from-brand-hover hover:to-brand-hover-dark text-white shadow-md"
            disabled={loading}
          >

            {loading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Send className="mr-2 h-4 w-4" />
            )}

            {loading
              ? "Running AuthEvidence Review..."
              : "Run Prior Authorization Review"}

          </Button>

        </form>

      </CardContent>
    </Card>
  );
}