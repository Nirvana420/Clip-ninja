import ClippedForm from "@/components/clipped/ClippedForm";
import { Scissors } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 bg-background">
      <header className="mb-8 text-center">
        <div className="flex items-center justify-center gap-3">
          <Scissors className="h-10 w-10 text-primary" />
          <h1 className="text-5xl font-bold font-headline text-foreground">
            Clip Ninja
          </h1>
        </div>
        <p className="text-muted-foreground mt-2">
          Your simple tool for YouTube video clipping.
        </p>
      </header>
      <ClippedForm />
    </main>
  );
}
