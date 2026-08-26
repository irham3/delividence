"use client";

import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import {
  ArrowRight,
  Check,
  FileAudio,
  FileText,
  Image as ImageIcon,
  LockKeyhole,
  MessageSquareText,
  PencilLine,
  ShieldCheck,
  Video,
} from "lucide-react";
import { ThemeToggle } from "@/components/delividence/theme-toggle";

gsap.registerPlugin(ScrollTrigger);

type LandingPageProps = {
  onSignIn: () => void;
  onSample: () => void;
  error?: string | null;
};

const sourceCards = [
  {
    label: "Email",
    icon: FileText,
    title: "Layout should be cleaner",
    body: "Keep the hero video muted. Reduce the copy.",
    caption: "What was said.",
  },
  {
    label: "Call",
    icon: FileAudio,
    title: "Start with the product",
    body: "No long intro. Show the working page first.",
    caption: "What was said.",
  },
  {
    label: "Screenshot",
    icon: ImageIcon,
    title: "Work that moves people",
    body: "Reference frame for tone and hierarchy.",
    caption: "What was shown.",
  },
  {
    label: "Video",
    icon: Video,
    title: "Hero reference",
    body: "Timestamped visual proof for review.",
    caption: "What was shown.",
  },
];

export function LandingPage({ onSignIn, onSample, error }: LandingPageProps) {
  const root = useRef<HTMLDivElement | null>(null);

  useGSAP(
    () => {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

      gsap.from(".hero-artifact", {
        y: 28,
        opacity: 0,
        rotate: (index) => [-2, 1.6, -1.2, 1][index] ?? 0,
        duration: 0.9,
        stagger: 0.12,
        ease: "power3.out",
      });

      gsap.from(".source-card", {
        y: 42,
        opacity: 0,
        stagger: 0.08,
        ease: "power3.out",
        scrollTrigger: {
          trigger: ".material-stage",
          start: "top 72%",
          end: "bottom 56%",
          scrub: 0.8,
        },
      });

      gsap.fromTo(
        ".change-route",
        { scaleX: 0, transformOrigin: "left center" },
        {
          scaleX: 1,
          ease: "none",
          scrollTrigger: {
            trigger: ".change-stage",
            start: "top 70%",
            end: "bottom 60%",
            scrub: 1,
          },
        }
      );
    },
    { scope: root }
  );

  return (
    <main ref={root} className="paper-texture min-h-[100dvh]">
      <header className="sticky top-0 z-30 border-b border-[var(--rule)] canvas-o88 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 sm:px-8">
          <a href="#" className="focus-ring text-lg font-semibold tracking-tight">
            Delividence
          </a>
          <nav className="hidden items-center gap-8 text-sm text-[var(--muted)] md:flex">
            <a className="focus-ring hover:text-[var(--ink)]" href="#workflow">
              Workflow
            </a>
            <a className="focus-ring hover:text-[var(--ink)]" href="#review">
              Review
            </a>
            <a className="focus-ring hover:text-[var(--ink)]" href="#about">
              About
            </a>
          </nav>
          <div className="flex items-center gap-3">
            <button className="tap focus-ring hidden text-sm text-[var(--muted)] hover:text-[var(--ink)] sm:inline-flex" onClick={onSignIn}>
              Sign in
            </button>
            <button
              className="tap focus-ring rounded-[6px] bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-[var(--accent-dark)]"
              onClick={onSignIn}
            >
              Create a record
            </button>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <section className="mx-auto grid min-h-[calc(100dvh-4rem)] max-w-7xl items-center gap-12 px-5 py-16 sm:px-8 lg:grid-cols-[0.9fr_1.1fr] lg:py-20">
        <div>
          <p className="max-w-44 border-l border-[var(--accent)] pl-3 text-sm italic leading-7 text-[var(--accent-dark)]">
            One place for the material behind the work
          </p>
          <h1 className="mt-9 max-w-[11ch] text-6xl font-semibold leading-[0.95] tracking-tight text-[var(--ink)] sm:text-7xl lg:text-8xl">
            The brief is more than the brief.
          </h1>
          <p className="mt-8 max-w-xl text-lg leading-8 text-[var(--muted)]">
            Emails, notes, images, and calls become a record the project can actually use.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-4">
            <button
              className="tap focus-ring rounded-[6px] bg-[var(--accent)] px-5 py-3 text-sm font-medium text-white hover:bg-[var(--accent-dark)]"
              onClick={onSignIn}
            >
              Create a record
            </button>
            <button
              className="tap focus-ring inline-flex items-center gap-2 border-b border-[var(--ink)] pb-1 text-sm font-medium"
              onClick={onSample}
            >
              See a sample <ArrowRight size={15} strokeWidth={1.8} />
            </button>
          </div>
          {error && <p className="mt-5 max-w-xl rounded-[6px] border border-[var(--danger)]/20 surface-o70 p-3 text-sm text-[var(--danger)]">{error}</p>}
        </div>

        <HeroArtifacts />
      </section>

      <section id="workflow" className="material-stage mx-auto max-w-7xl px-5 py-24 sm:px-8 lg:py-32">
        <h2 className="max-w-3xl text-4xl font-semibold tracking-tight sm:text-5xl">
          Watch the material become a record.
        </h2>
        <div className="mt-14 grid gap-8 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="grid gap-4 sm:grid-cols-2">
            {sourceCards.map((item) => (
              <article key={item.label} className="source-card paper-card min-h-52 rounded-[8px] p-5">
                <div className="flex items-center justify-between">
                  <span className="mono text-xs uppercase tracking-[0.12em] text-[var(--muted)]">{item.label}</span>
                  <item.icon size={18} strokeWidth={1.7} className="text-[var(--accent)]" />
                </div>
                <h3 className="mt-8 text-2xl font-semibold tracking-tight">{item.title}</h3>
                <p className="mt-3 text-sm leading-6 text-[var(--muted)]">{item.body}</p>
                <p className="mt-8 text-sm text-[var(--ink)]">{item.caption}</p>
              </article>
            ))}
          </div>
          <ProjectRecordCard />
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-24 sm:px-8 lg:py-32">
        <div className="grid gap-10 lg:grid-cols-[0.85fr_1.15fr]">
          <div>
            <h2 className="text-4xl font-semibold tracking-tight sm:text-5xl">
              The record asks for a decision, not another conversation.
            </h2>
            <p className="mt-6 max-w-lg text-lg leading-8 text-[var(--muted)]">
              The agent narrows the unresolved parts. The client chooses what they meant.
            </p>
          </div>
          <div className="paper-card record-shadow rounded-[8px] p-6">
            <div className="grid gap-5 lg:grid-cols-[1fr_0.8fr]">
              <div>
                <p className="mono text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Unresolved question</p>
                <h3 className="mt-5 text-3xl font-semibold tracking-tight">
                  Should the hero video be 20 seconds or 30 seconds?
                </h3>
                <div className="mt-7 space-y-3 text-sm text-[var(--muted)]">
                  <p className="rounded-[6px] border border-[var(--rule)] surface-o50 p-3">S-02 Call: “keep the intro short”</p>
                  <p className="rounded-[6px] border border-[var(--rule)] surface-o50 p-3">S-04 Email: “give us a slightly longer cut”</p>
                </div>
              </div>
              <div className="rounded-[8px] border border-[var(--rule)] bg-[var(--surface-strong)] p-5">
                <p className="text-sm font-medium">Client reply</p>
                <div className="mt-5 space-y-3">
                  <button className="focus-ring tap flex w-full items-center justify-between rounded-[6px] border border-[var(--accent)] bg-[var(--accent-soft)] px-4 py-3 text-left text-sm">
                    20 seconds <Check size={17} strokeWidth={1.8} />
                  </button>
                  <button className="focus-ring tap w-full rounded-[6px] border border-[var(--rule)] px-4 py-3 text-left text-sm text-[var(--muted)]">
                    30 seconds
                  </button>
                </div>
                <p className="mt-6 text-sm leading-6 text-[var(--muted)]">
                  Only the client resolves conflicting client statements.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="change-stage mx-auto max-w-7xl px-5 py-24 sm:px-8 lg:py-32">
        <h2 className="max-w-3xl text-4xl font-semibold tracking-tight sm:text-5xl">
          New work takes a separate path.
        </h2>
        <div className="mt-14 grid items-center gap-6 lg:grid-cols-[1fr_0.45fr_1fr]">
          <PaperNote title="Baseline stays." lines={["Header simplified", "Hero video starts muted", "Button label: Get in touch"]} />
          <div className="relative min-h-28">
            <div className="absolute left-1/2 top-0 h-full w-px bg-[var(--ink)]/40" />
            <div className="change-route absolute left-0 top-1/2 h-[2px] w-full bg-[var(--accent)]" />
          </div>
          <PaperNote title="Decision is recorded." lines={["Request: add testimonials", "Impact: below the fold", "Approved by: client"]} accent />
        </div>
        <p className="mt-8 max-w-3xl text-base leading-7 text-[var(--muted)]">
          The confirmed baseline stays intact. New requests become field notes and formal change decisions.
        </p>
      </section>

      <section id="review" className="mx-auto max-w-7xl px-5 py-24 sm:px-8 lg:py-32">
        <div className="grid gap-8 lg:grid-cols-[0.7fr_1.3fr]">
          <div className="paper-card sticky top-24 h-fit rounded-[8px] p-6">
            <p className="mono text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Active criterion</p>
            <h2 className="mt-5 text-3xl font-semibold tracking-tight">Put the proof beside the promise.</h2>
            <p className="mt-5 text-sm leading-6 text-[var(--muted)]">
              Visual checks assist the review. The client decides.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {["Final screenshot", "Video reference", "Mobile capture", "Client note"].map((item, index) => (
              <div key={item} className="paper-card rounded-[8px] p-5">
                <div className="flex h-40 items-center justify-center rounded-[6px] border border-[var(--rule)] bg-[var(--surface-strong)]">
                  {index === 1 ? <Video size={36} strokeWidth={1.5} /> : <ImageIcon size={36} strokeWidth={1.5} />}
                </div>
                <div className="mt-4 flex items-center justify-between text-sm">
                  <span>{item}</span>
                  <span className="mono text-xs text-[var(--muted)]">S-0{index + 2}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="about" className="mx-auto max-w-7xl px-5 py-24 sm:px-8 lg:py-32">
        <div className="grid border-y border-[var(--rule)] md:grid-cols-3">
          {[
            ["Source linked", "Every point in the record links back to what was said or shown."],
            ["Workflow resumed", "Pause, return, and continue without losing context."],
            ["Version retained", "Every change, decision, and handoff is recorded with time and author."],
          ].map(([title, body]) => (
            <div key={title} className="border-[var(--rule)] py-8 md:border-r md:px-8 md:last:border-r-0">
              <h3 className="font-semibold">{title}</h3>
              <p className="mt-3 max-w-sm text-sm leading-6 text-[var(--muted)]">{body}</p>
            </div>
          ))}
        </div>
        <p className="mt-8 text-center text-sm text-[var(--muted)]">
          Built with Gemini 3.5, Google ADK, and Google Cloud.
        </p>
        <div className="mt-16 text-center">
          <h2 className="text-4xl font-semibold tracking-tight">Give the work a record worth returning to.</h2>
          <button
            className="tap focus-ring mt-8 rounded-[6px] bg-[var(--accent)] px-5 py-3 text-sm font-medium text-white hover:bg-[var(--accent-dark)]"
            onClick={onSignIn}
          >
            Create a record
          </button>
        </div>
      </section>

      <footer className="mx-auto flex max-w-7xl flex-col gap-4 border-t border-[var(--rule)] px-5 py-8 text-sm text-[var(--muted)] sm:px-8 md:flex-row md:items-center md:justify-between">
        <span>© 2026 Delividence</span>
        <span>hello@delividence.com</span>
      </footer>
    </main>
  );
}

function HeroArtifacts() {
  return (
    <div className="relative min-h-[560px]">
      <div aria-hidden className="absolute right-10 top-1 h-28 w-6 rotate-[18deg] rounded-full border border-[var(--ink)]/30" />
      <div aria-hidden className="absolute bottom-6 right-0 h-72 w-5 rotate-[11deg] rounded-full bg-[var(--ink)] shadow-xl" />
      <div className="hero-artifact paper-card absolute left-2 top-8 w-[46%] rotate-[-1deg] rounded-[6px] p-5">
        <p className="mono text-[10px] uppercase tracking-[0.12em] text-[var(--muted)]">Email</p>
        <p className="mt-4 text-sm leading-6">Let&apos;s keep the layout clean and the headline lighter.</p>
        <p className="mt-6 text-sm">- Alina</p>
      </div>
      <div className="hero-artifact paper-card absolute right-0 top-16 w-[46%] rotate-[1deg] rounded-[6px] p-5">
        <p className="mono text-[10px] uppercase tracking-[0.12em] text-[var(--muted)]">Call transcript</p>
        <p className="mt-4 text-sm leading-6">Start with the product. Also, reduce the copy.</p>
        <div className="mt-5 h-8 rounded bg-[repeating-linear-gradient(90deg,var(--ink)_0_2px,transparent_2px_10px)] opacity-60" />
      </div>
      <div className="hero-artifact paper-card absolute bottom-20 left-8 w-[50%] rotate-[1.4deg] rounded-[6px] p-5">
        <p className="mono text-[10px] uppercase tracking-[0.12em] text-[var(--muted)]">Hero reference</p>
        <h3 className="mt-4 text-2xl font-semibold tracking-tight">Work that moves people.</h3>
        <div className="mt-5 flex h-28 items-center justify-center rounded-[4px] bg-[linear-gradient(135deg,#d7d1c5,#87928d)]">
          <span className="rounded-full surface-o75 px-3 py-2 text-xs">Play</span>
        </div>
      </div>
      <div className="hero-artifact paper-card absolute bottom-8 right-2 w-[42%] rotate-[-1deg] rounded-[6px] p-5">
        <p className="mono text-[10px] uppercase tracking-[0.12em] text-[var(--muted)]">Source index</p>
        {["Email", "Call", "Screenshot", "Brief"].map((item, index) => (
          <div key={item} className="mt-3 flex items-center justify-between border-b border-[var(--rule)] pb-2 text-xs">
            <span>S-0{index + 1}</span>
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ProjectRecordCard() {
  return (
    <article className="paper-card record-shadow rounded-[8px] p-6">
      <div className="flex items-center justify-between">
        <p className="mono text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Project record</p>
        <LockKeyhole size={18} strokeWidth={1.7} className="text-[var(--accent)]" />
      </div>
      <h3 className="mt-8 text-3xl font-semibold tracking-tight">Project Agreement</h3>
      <ul className="mt-7 space-y-4 text-sm leading-6 text-[var(--muted)]">
        <li>Header is simplified and copy is reduced.</li>
        <li>Hero video starts muted.</li>
        <li>Button label is “Get in touch”.</li>
        <li>Footer includes contact details and social links.</li>
      </ul>
      <div className="mt-8 grid grid-cols-2 gap-3">
        <div className="rounded-[6px] border border-[var(--rule)] p-3">
          <PencilLine size={18} strokeWidth={1.7} className="text-[var(--accent)]" />
          <p className="mt-3 text-sm">Editable until approved</p>
        </div>
        <div className="rounded-[6px] border border-[var(--rule)] p-3">
          <ShieldCheck size={18} strokeWidth={1.7} className="text-[var(--accepted)]" />
          <p className="mt-3 text-sm">Versioned after approval</p>
        </div>
      </div>
    </article>
  );
}

function PaperNote({ title, lines, accent = false }: { title: string; lines: string[]; accent?: boolean }) {
  return (
    <article className={`paper-card rounded-[8px] p-6 ${accent ? "border-[var(--accent)]" : ""}`}>
      <p className="mono text-xs uppercase tracking-[0.12em] text-[var(--muted)]">{title}</p>
      <div className="mt-7 space-y-4">
        {lines.map((line) => (
          <p key={line} className="flex items-start gap-3 text-sm leading-6">
            <MessageSquareText size={16} strokeWidth={1.7} className="mt-1 shrink-0 text-[var(--accent)]" />
            {line}
          </p>
        ))}
      </div>
    </article>
  );
}
