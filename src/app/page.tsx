import ClippedForm from "@/components/clipped/ClippedForm";
import { Scissors } from "lucide-react";
import Head from "next/head";

export default function Home() {
  return (
    <>
      <Head>
        <title>Clip Ninja - YouTube Video Clipper & Downloader</title>
        <meta
          name="description"
          content="Clip Ninja is the easiest way to trim and download YouTube video clips. Paste a YouTube link, select your time range, and get your video instantly!"
        />
        <meta
          name="keywords"
          content="YouTube clipper, YouTube downloader, video trimmer, download YouTube clip, YouTube video cutter, YouTube to mp4, YouTube short clip, online video trimmer"
        />
        <meta name="robots" content="index, follow" />
        <meta
          property="og:title"
          content="Clip Ninja - YouTube Video Clipper & Downloader"
        />
        <meta
          property="og:description"
          content="Trim and download YouTube video clips instantly. No signup required!"
        />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://clip.ninja/" />
        <meta property="og:image" content="/favicon.ico" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta
          name="twitter:title"
          content="Clip Ninja - YouTube Video Clipper & Downloader"
        />
        <meta
          name="twitter:description"
          content="Trim and download YouTube video clips instantly. No signup required!"
        />
        <meta name="twitter:image" content="/favicon.ico" />
        <link rel="canonical" href="https://clip.ninja/" />
      </Head>
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
    </>
  );
}
