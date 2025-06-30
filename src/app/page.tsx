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
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              name: "Clip Ninja",
              url: "https://clip.ninja/",
              applicationCategory: "VideoApplication",
              operatingSystem: "All",
              description:
                "Clip Ninja is the easiest way to trim and download YouTube video clips. Paste a YouTube link, select your time range, and get your video instantly!",
              offers: {
                "@type": "Offer",
                price: "0",
                priceCurrency: "USD",
                availability: "https://schema.org/InStock",
              },
              aggregateRating: {
                "@type": "AggregateRating",
                ratingValue: "4.8",
                reviewCount: "120",
              },
            }),
          }}
        />
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
                                          {/* SEO Keyword Cards Section */}
      <section className="w-full flex flex-col items-center bg-muted py-10 mt-8">
        <h2 className="text-2xl font-bold mb-6 text-center text-foreground">
          Why Use Clip Ninja?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl px-4">
          <div className="bg-background rounded-lg shadow p-6 border border-border flex flex-col items-center">
            <h3 className="text-lg font-semibold mb-2 text-primary">
              YouTube Clip Cutter
            </h3>
            <p className="text-muted-foreground text-center">
              Effortlessly cut and extract the best moments from any YouTube video
              with our YouTube clip cutter. Perfect for sharing highlights or
              saving your favorite scenes.
            </p>
          </div>
          <div className="bg-background rounded-lg shadow p-6 border border-border flex flex-col items-center">
            <h3 className="text-lg font-semibold mb-2 text-primary">
              Trim YouTube Videos Online
            </h3>
            <p className="text-muted-foreground text-center">
              Trim YouTube videos online in seconds—no downloads or signups
              required. Just paste your link, select the time range, and get your
              trimmed video instantly.
            </p>
          </div>
          <div className="bg-background rounded-lg shadow p-6 border border-border flex flex-col items-center">
            <h3 className="text-lg font-semibold mb-2 text-primary">
              Download YouTube Segments
            </h3>
            <p className="text-muted-foreground text-center">
              Download YouTube segments and create video highlights for TikTok,
              Instagram, or any platform. The best tool to extract clips from
              YouTube for TikTok and more!
            </p>
          </div>
        </div>
      </section>
        {/* Disclaimer Section */}
      <footer className="w-full flex flex-col items-center mt-6 mb-2 px-4">
        <div className="max-w-3xl text-xs text-center text-muted-foreground bg-background border border-border rounded p-4">
          <strong>Disclaimer:</strong> Clip Ninja is intended for personal and
          educational use only. Users are solely responsible for ensuring their
          use of this tool complies with YouTube’s{" "}
          <a
            href="https://www.youtube.com/static?template=terms"
            target="_blank"
            rel="noopener noreferrer"
            className="underline"
          >
            Terms of Service
          </a>{" "}
          and all applicable copyright laws. Do not download, share, or distribute
          content without proper authorization from the copyright owner. The
          creators of Clip Ninja are not liable for any misuse of this service.
        </div>
      </footer>
    </>
  );
}
