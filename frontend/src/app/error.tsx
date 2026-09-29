"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";
import Link from "next/link";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service like Sentry
    console.error(error);
  }, [error]);

  return (
    <div className="flex h-screen w-full flex-col items-center justify-center space-y-4 bg-background px-4 text-center">
      <AlertCircle className="h-12 w-12 text-destructive" />
      <h2 className="text-2xl font-bold tracking-tight">Something went wrong!</h2>
      <p className="text-muted-foreground max-w-md">
        An unexpected error has occurred. We've been notified and are looking into it.
      </p>
      <div className="flex gap-4 mt-6">
        <Button onClick={() => reset()}>Try again</Button>
        <Button variant="outline" render={<Link href="/" />}>Go back home</Button>
      </div>
    </div>
  );
}
