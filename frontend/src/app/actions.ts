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
  documentContent?: string;
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

  const file = formData.get("file") as File | null;
  const text = formData.get("text") as string;
  const documentContent = formData.get("documentContent") as string;

  if ((!file || !file.size) && !text && !documentContent) {
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
  
  let newDocumentContent: string | undefined = documentContent;

  if (file && file.size > 0) {
    // If a new file is uploaded, use it.
    apiFormData.append('file', file);
    // We can't easily read file content on the server action, so we'll pass it back
    // This is a simplified approach; a real app might handle this differently.
    // For now, we'll just signal that content is present from the file.
    newDocumentContent = await file.text();
  } else if (text) {
    // If text is pasted, use it.
    apiFormData.append('text', text);
    newDocumentContent = text;
  } else if (documentContent) {
    // If no new file/text, use the persisted content.
    apiFormData.append('text', documentContent);
    newDocumentContent = documentContent;
  }


  try {
    const result = await callFastAPI(apiFormData);
    return { type: "success", result, mode: result.mode, documentContent: newDocumentContent };

  } catch (error) {
    console.error(error);
    const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
    return { type: "error", message: `API call failed: ${errorMessage}`, documentContent: newDocumentContent };
  }
}
