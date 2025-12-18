"use server";

import { z } from "zod";

const formSchema = z.object({
  mode: z.enum(["qa", "section", "summary"]),
  question: z.string().optional(),
});

export type FormState = {
  type: "success" | "error";
  result?: any;
  message?: string;
  mode?: "qa" | "section" | "summary";
} | null;


async function callFastAPI(formData: FormData) {
    const backendUrl = process.env.FASTAPI_BACKEND_URL;

    if (!backendUrl) {
        throw new Error("FASTAPI_BACKEND_URL is not set in the environment variables.");
    }
    
    const endpoint = "/document/process";

    const response = await fetch(`${backendUrl}${endpoint}`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const errorBody = await response.text();
        try {
            const errorJson = JSON.parse(errorBody);
            throw new Error(errorJson.detail || `FastAPI request failed with status ${response.status}`);
        } catch {
            throw new Error(`FastAPI request failed with status ${response.status}: ${errorBody}`);
        }
    }

    return await response.json();
}

export async function handleDocumentAction(
  prevState: FormState,
  formData: FormData
): Promise<FormState> {

  const file = formData.get("file") as File;
  const text = formData.get("text") as string;

  if (!file.size && !text) {
    return {
      type: "error",
      message: "Please upload a document or paste text to analyze.",
    };
  }

  const validatedFields = formSchema.safeParse({
    mode: formData.get("mode"),
    question: formData.get("question"),
  });

  if (!validatedFields.success) {
    return {
      type: "error",
      message: "Invalid form data: " + validatedFields.error.flatten().formErrors.join(', '),
    };
  }

  const { mode, question } = validatedFields.data;

  if (mode === 'qa' && !question) {
    return {
      type: 'error',
      message: 'A question is required for "Ask Question" mode.'
    }
  }

  const apiFormData = new FormData();
  apiFormData.append('mode', mode);
  if (question) {
    apiFormData.append('question', question);
  }
  if (file && file.size > 0) {
    apiFormData.append('file', file);
  }
  if (text) {
    apiFormData.append('text', text);
  }


  try {
    const result = await callFastAPI(apiFormData);
    return { type: "success", result, mode: result.mode };

  } catch (error) {
    console.error(error);
    const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
    return { type: "error", message: `API call failed: ${errorMessage}` };
  }
}
