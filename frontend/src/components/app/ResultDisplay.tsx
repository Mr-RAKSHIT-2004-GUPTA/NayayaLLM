"use client";

import { useFormStatus } from "react-dom";
import { Loader2, BookText, Bot } from "lucide-react";
import type { FormState } from "@/app/actions";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

interface ResultDisplayProps {
  formState: FormState;
}

export function ResultDisplay({ formState }: ResultDisplayProps) {
  const { pending } = useFormStatus();

  if (pending) {
    return (
      <div className="space-y-4 pt-4">
        <div className="flex items-center gap-3 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin text-primary" />
          <span className="font-medium">Generating analysis... This may take a moment.</span>
        </div>
        <div className="space-y-3 pt-4">
          <div className="h-4 bg-muted/50 rounded w-3/4 animate-pulse"></div>
          <div className="h-4 bg-muted/50 rounded w-full animate-pulse"></div>
          <div className="h-4 bg-muted/50 rounded w-5/6 animate-pulse"></div>
          <div className="h-4 bg-muted/50 rounded w-1/2 animate-pulse mt-6"></div>
          <div className="h-4 bg-muted/50 rounded w-full animate-pulse"></div>
          <div className="h-4 bg-muted/50 rounded w-full animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (!formState || formState.type === "error") {
    return (
      <div className="flex h-full min-h-[50vh] flex-col items-center justify-center text-center text-muted-foreground">
        <Bot className="w-16 h-16 mb-4 opacity-30" />
        <h3 className="font-headline text-xl font-semibold text-foreground">Your results will appear here</h3>
        <p className="max-w-xs mt-2 text-sm">
          Provide a document and select an analysis mode to get started.
        </p>
      </div>
    );
  }

  const { result, mode } = formState;

  if (!result) {
     return (
      <div className="flex h-full min-h-[50vh] flex-col items-center justify-center text-center text-muted-foreground">
        <Bot className="w-16 h-16 mb-4 opacity-30" />
        <h3 className="font-headline text-xl font-semibold">No results returned</h3>
        <p className="max-w-xs mt-2 text-sm">
          The analysis completed, but the backend did not return any data.
        </p>
      </div>
    );
  }

  return (
    <div className="prose prose-sm dark:prose-invert max-w-none text-foreground prose-headings:font-headline prose-p:leading-relaxed prose-headings:text-foreground prose-strong:text-foreground">
      {mode === "summary" && typeof result.summary === "string" && (
        <>
          <h3><Badge variant="secondary">Complete Summary</Badge></h3>
          <ScrollArea className="h-96 rounded-md border border-border/50 bg-background/20 p-4 mt-4">
            <p>{result.summary}</p>
          </ScrollArea>
        </>
      )}
      {mode === "qa" && typeof result.answer === "string" && (
        <>
          <h3><Badge variant="secondary">Answer</Badge></h3>
          <div className="mt-4 rounded-md border border-border/50 bg-background/20 p-4">
            <p>{result.answer}</p>
          </div>
        </>
      )}
      {mode === "section" && typeof result.sections === 'object' && result.sections !== null && (
        <>
          <h3><Badge variant="secondary">Section-wise Summaries</Badge></h3>
          <Accordion type="single" collapsible className="w-full not-prose mt-4 space-y-2">
            {Object.entries(result.sections).map(([sectionTitle, sectionSummary], index) => (
              <AccordionItem value={`item-${index}`} key={index} className="rounded-md border border-border/50 bg-background/20 px-4">
                <AccordionTrigger className="text-left font-semibold text-foreground hover:no-underline">
                    {sectionTitle}
                </AccordionTrigger>
                <AccordionContent className="prose prose-sm dark:prose-invert">
                  {typeof sectionSummary === 'string' ? sectionSummary : JSON.stringify(sectionSummary)}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </>
      )}
    </div>
  );
}
