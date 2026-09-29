import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex h-screen w-full flex-col items-center justify-center space-y-4 bg-background px-4 text-center">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">404</h1>
      <h2 className="text-2xl font-semibold tracking-tight">Page not found</h2>
      <p className="text-muted-foreground max-w-md">
        Sorry, we couldn't find the page you're looking for. It might have been removed or the link might be broken.
      </p>
      <div className="pt-4">
        <Button render={<Link href="/" />}>
          Return Home
        </Button>
      </div>
    </div>
  );
}
