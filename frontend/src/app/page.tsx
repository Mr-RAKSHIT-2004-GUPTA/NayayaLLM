"use client";

import { useRef, useEffect, useState } from "react";
import { useActionState } from "react";
import {
  FileText,
  Upload,
  Sparkles,
  BookText,
  ListCollapse,
  X,
  FileUp,
  BrainCircuit,
  CheckCircle2
} from "lucide-react";

import { handleDocumentAction, type FormState } from "@/app/actions";
import { Logo } from "@/components/icons";
import { SubmitButton } from "@/components/SubmitButton";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { ResultDisplay } from "@/components/app/ResultDisplay";
import { ThemeToggle } from "@/components/ThemeToggle";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

const initialState: FormState = null;

export default function Home() {
  const [formState, formAction] = useActionState(
    handleDocumentAction,
    initialState
  );

  const formRef = useRef<HTMLFormElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string>('');
  
  // We need this state to force re-render when inputs are cleared.
  const [inputVersion, setInputVersion] = useState(0);

  const { toast } = useToast();

  useEffect(() => {
    if (formState?.type === "error") {
      toast({
        variant: "destructive",
        title: "Error",
        description: formState.message,
      });
    }
  }, [formState, toast]);

  const clearInputs = () => {
    if (formRef.current) {
      formRef.current.reset();
    }
    setFileName('');
    if (fileInputRef.current) {
        fileInputRef.current.value = "";
    }
    setInputVersion(v => v + 1);
  };
  
  return (
    <div className="flex min-h-screen w-full flex-col bg-background selection:bg-primary/20">
       <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border/50 bg-background/80 px-4 backdrop-blur-sm sm:px-6">
        <div className="flex items-center gap-2">
          <Logo className="h-8 w-8 text-primary" />
          <h1 className="font-headline text-xl font-bold tracking-tighter text-foreground sm:text-2xl">
            NayayaLLM
          </h1>
        </div>
        <p className="hidden text-sm italic text-muted-foreground md:block">
          Legal Document Intelligence
        </p>
        <div className="ml-auto">
          <ThemeToggle />
        </div>
      </header>

      <main className="flex-1 p-4 sm:p-6 md:p-8">
        <form
          ref={formRef}
          action={formAction}
          className="grid items-start gap-8 lg:grid-cols-2"
          key={inputVersion}
        >
          <div className="lg:sticky lg:top-24 space-y-8">
            <Card className="bg-card/50 shadow-lg shadow-primary/5">
              <CardHeader>
                <CardTitle className="font-headline text-2xl tracking-tight flex items-center gap-2">
                  <FileText className="w-6 h-6" />
                  <span>Analyze Document</span>
                </CardTitle>
                <CardDescription>
                  Upload a file or paste text. The AI will process it based on
                  your selected mode.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                 <div className="relative">
                    <Textarea
                      name="text"
                      placeholder="Paste your legal document text here..."
                      className="min-h-[250px] resize-y pr-10 focus:ring-1 focus:ring-primary/80"
                    />
                     <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute top-2 right-2 h-7 w-7 text-muted-foreground hover:text-foreground"
                        onClick={clearInputs}
                      >
                        <X className="h-4 w-4" />
                        <span className="sr-only">Clear input</span>
                      </Button>
                  </div>
                
                <div className="flex items-center text-sm text-muted-foreground">
                  <div className="flex-grow border-t border-border/50"></div>
                  <span className="mx-4 flex-shrink text-xs uppercase">Or</span>
                  <div className="flex-grow border-t border-border/50"></div>
                </div>

                <div className="w-full">
                  <Label
                    htmlFor="file-upload"
                    className="flex w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-border/50 bg-background/50 p-6 text-center transition hover:border-primary/80 hover:bg-primary/5"
                  >
                    {fileName ? (
                       <>
                        <CheckCircle2 className="h-8 w-8 text-green-500" />
                        <p className="mt-2 text-sm font-semibold text-foreground">
                          {fileName}
                        </p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          File ready to be analyzed.
                        </p>
                      </>
                    ) : (
                      <>
                        <FileUp className="h-8 w-8 text-muted-foreground" />
                        <p className="mt-2 text-sm text-foreground">
                          <span className="font-semibold text-primary">
                            Click to upload
                          </span>{" "}
                          a document
                        </p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          TXT or PDF files accepted
                        </p>
                      </>
                    )}
                     <Input
                      id="file-upload"
                      ref={fileInputRef}
                      name="file"
                      type="file"
                      className="hidden"
                      accept=".txt,.pdf"
                      onChange={(e) => setFileName(e.target.files?.[0]?.name || '')}
                    />
                  </Label>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-card/50 shadow-lg shadow-primary/5">
                <CardHeader>
                    <CardTitle className="font-headline text-2xl tracking-tight flex items-center gap-2">
                        <BrainCircuit className="w-6 h-6"/>
                        <span>Select Analysis Mode</span>
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                     <RadioGroup
                        defaultValue="qa"
                        name="mode"
                        className="grid grid-cols-1 gap-3 sm:grid-cols-3"
                      >
                       <Label className="relative flex cursor-pointer items-center justify-center gap-2 rounded-md border-2 border-border/50 bg-transparent p-3 font-semibold transition-all hover:bg-accent/10 has-[:checked]:border-primary has-[:checked]:bg-primary has-[:checked]:text-primary-foreground has-[:checked]:shadow-[0_0_15px_hsl(var(--primary))]">
                           <RadioGroupItem value="qa" id="mode-qa" className="peer sr-only" />
                           <Sparkles className="h-5 w-5" />
                           <span>Ask Question</span>
                        </Label>
                        <Label className="relative flex cursor-pointer items-center justify-center gap-2 rounded-md border-2 border-border/50 bg-transparent p-3 font-semibold transition-all hover:bg-accent/10 has-[:checked]:border-primary has-[:checked]:bg-primary has-[:checked]:text-primary-foreground has-[:checked]:shadow-[0_0_15px_hsl(var(--primary))]">
                           <RadioGroupItem value="section" id="mode-section" className="peer sr-only" />
                           <ListCollapse className="h-5 w-5" />
                           <span>Summarise Sections</span>
                        </Label>
                        <Label className="relative flex cursor-pointer items-center justify-center gap-2 rounded-md border-2 border-border/50 bg-transparent p-3 font-semibold transition-all hover:bg-accent/10 has-[:checked]:border-primary has-[:checked]:bg-primary has-[:checked]:text-primary-foreground has-[:checked]:shadow-[0_0_15px_hsl(var(--primary))]">
                            <RadioGroupItem value="summary" id="mode-summary" className="peer sr-only" />
                            <BookText className="h-5 w-5" />
                            <span>Summary</span>
                        </Label>
                      </RadioGroup>

                      <div className="pt-2">
                        <Label htmlFor="question" className="text-muted-foreground">Your Question</Label>
                        <Input
                          id="question"
                          name="question"
                          placeholder="e.g., What are the termination clauses?"
                          className="mt-1 bg-background/50 focus:ring-1 focus:ring-primary/80"
                        />
                      </div>
                      
                      <SubmitButton className="w-full text-lg font-bold" size="lg">
                        Analyze Now
                      </SubmitButton>
                </CardContent>
            </Card>

          </div>

          <Card className="min-h-[80vh] bg-card/50 shadow-lg shadow-primary/5">
            <CardHeader>
              <CardTitle className="font-headline text-2xl tracking-tight">
                AI Analysis
              </CardTitle>
              <CardDescription>
                The generated insights based on your document will appear below.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResultDisplay formState={formState} />
            </CardContent>
          </Card>
        </form>
      </main>
    </div>
  );
}
