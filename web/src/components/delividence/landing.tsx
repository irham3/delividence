"use client";

import { useRef } from "react";
import Image from "next/image";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import {
  ArrowDown,
  AudioLines,
  Check,
  ChevronRight,
  Copy,
  ExternalLink,
  FileText,
  Image as ImageIcon,
  Mail,
  Play,
  Plus,
  Video,
} from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

type LandingPageProps = {
  onSignIn: () => void;
  onSample: () => void;
  error?: string | null;
};

const agreementItems = [
  "Simplify the header and reduce copy.",
  "Start the hero video muted.",
  "Button label: “Get in touch”.",
  "Maintain clean layout and lighter headline weight.",
];

const sourceFiles = [
  ["email_sarah_0429.eml", "Apr 29, 9:14 AM", "mail"],
  ["call_0429.mp3", "Apr 29, 10:02 AM", "audio"],
  ["hero_v2.png", "Apr 29, 10:11 AM", "image"],
  ["brief_project.pdf", "Apr 28, 4:22 PM", "file"],
  ["hero_ref.mp4", "Apr 27, 2:18 PM", "video"],
];

export function LandingPage({ onSignIn, onSample, error }: LandingPageProps) {
  const root = useRef<HTMLDivElement | null>(null);

  useGSAP(
    () => {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
      const mm = gsap.matchMedia();

      const premiumEase = "power3.out";

      gsap.timeline({ defaults: { ease: premiumEase } })
        .from(".site-header-inner", { y: -18, autoAlpha: 0, duration: 0.65 })
        .from(".hero-copy > *", { y: 28, autoAlpha: 0, duration: 0.78, stagger: 0.075 }, 0.12)
        .from(".hero-artifact", {
          y: 38,
          x: (index) => (index % 2 === 0 ? -14 : 14),
          rotate: (index) => [-2.2, 1.6, -1.2, 1][index] ?? 0,
          autoAlpha: 0,
          duration: 0.92,
          stagger: 0.085,
        }, 0.18);

      gsap.timeline({
        scrollTrigger: {
          trigger: ".hero-stage",
          start: "top top",
          end: "bottom top",
          scrub: 1.15,
        },
      })
        .to(".hero-copy", { y: -54, autoAlpha: 0.32, scale: 0.986, ease: "none" }, 0)
        .to(".hero-art-board", { y: 66, scale: 0.982, ease: "none" }, 0)
        .to(".hero-artifact", { y: (index) => 22 + index * 5, rotate: (index) => (index % 2 ? 0.7 : -0.7), ease: "none" }, 0);

      gsap.fromTo(".scroll-progress", { scaleY: 0, transformOrigin: "top center" }, {
        scaleY: 1,
        ease: "none",
        scrollTrigger: { trigger: root.current, start: "top top", end: "bottom bottom", scrub: 0.3 },
      });

      gsap.utils.toArray<HTMLElement>(".editorial-section").forEach((section) => {
        const heading = section.querySelector(".section-heading");
        if (heading) {
          gsap.timeline({ scrollTrigger: { trigger: section, start: "top 79%", toggleActions: "play none none reverse" } })
            .from(heading.querySelector(".section-number"), { y: 18, autoAlpha: 0, duration: 0.58, ease: premiumEase })
            .from(heading.querySelector(".section-title"), { y: 28, clipPath: "inset(0 0 100% 0)", duration: 0.72, ease: premiumEase }, 0.04)
            .from(heading.querySelector(".section-heading-rule"), { scaleX: 0, transformOrigin: "left center", duration: 0.82, ease: "power2.inOut" }, 0.08);
        }

        gsap.to(section, {
          y: -18,
          autoAlpha: 0.68,
          scale: 0.994,
          transformOrigin: "center top",
          ease: "none",
          scrollTrigger: { trigger: section, start: "bottom 34%", end: "bottom top", scrub: 0.8 },
        });
      });

      gsap.utils.toArray<HTMLElement>(".journey-connector").forEach((connector) => {
        const progress = connector.querySelector(".journey-progress");
        const arrow = connector.querySelector(".journey-arrow");
        const label = connector.querySelector(".journey-label");
        gsap.timeline({ scrollTrigger: { trigger: connector, start: "top 88%", end: "bottom 42%", scrub: 0.72 } })
          .fromTo(progress, { scaleY: 0, transformOrigin: "top center" }, { scaleY: 1, ease: "none" }, 0)
          .fromTo(arrow, { y: 0, autoAlpha: 0.2 }, { y: 76, autoAlpha: 1, ease: "none" }, 0)
          .from(label, { x: -8, autoAlpha: 0, ease: "power2.out" }, 0.5);
      });

      mm.add("(min-width: 1024px)", () => {
        gsap.timeline({ scrollTrigger: { trigger: ".material-stage", start: "top 76%", end: "top 19%", scrub: 1.1 } })
          .from(".scene-two-source", { y: 84, x: (index) => (index - 2) * 18, rotate: (index) => [-4, 2.5, -1.5, 2.5, -2][index] ?? 0, scale: 0.94, autoAlpha: 0.28, stagger: 0.075, ease: "power2.out" }, 0)
          .from(".project-record-panel", { x: 72, clipPath: "inset(0 0 0 100%)", autoAlpha: 0.35, ease: "power2.inOut" }, 0.16)
          .from(".project-record-bracket", { scaleY: 0, transformOrigin: "top center", ease: "none" }, 0.54)
          .fromTo(".source-progress", { scaleX: 0, transformOrigin: "left center" }, { scaleX: 1, ease: "none" }, 0.14)
          .fromTo(".source-arrow", { x: -22, autoAlpha: 0 }, { x: 0, autoAlpha: 1, ease: "none" }, 0.48);

        gsap.timeline({ scrollTrigger: { trigger: "#clarification", start: "top 76%", end: "top 20%", scrub: 1.05 } })
          .from(".process-panel", { y: 72, clipPath: "inset(0 0 16% 0)", autoAlpha: 0.22, stagger: 0.12, ease: "power2.out" })
          .from(".process-panel > *", { y: 16, autoAlpha: 0.45, stagger: 0.025, ease: "power2.out" }, 0.18)
          .fromTo(".client-handoff-arrow", { scaleX: 0, transformOrigin: "left center", autoAlpha: 0 }, { scaleX: 1, autoAlpha: 1, ease: "none" }, 0.54);

        gsap.timeline({ scrollTrigger: { trigger: ".decision-stage", start: "top 76%", end: "top 17%", scrub: 1.12 } })
          .from(".decision-paper-wrap", { y: 96, x: (index) => [-38, 0, 38][index] ?? 0, rotate: (index) => [-2.4, 1.3, -1.2][index] ?? 0, scale: 0.94, autoAlpha: 0.25, stagger: 0.11, ease: "power2.out" }, 0)
          .fromTo(".decision-route", { scaleX: 0, transformOrigin: "left center" }, { scaleX: 1, ease: "none" }, 0.3)
          .fromTo(".decision-arrow", { left: "7%", autoAlpha: 0 }, { left: "90%", autoAlpha: 1, ease: "none" }, 0.3)
          .from(".decision-paper", { boxShadow: "0 2px 4px rgb(32 33 31 / 0.02)", stagger: 0.08, ease: "none" }, 0.26);

        gsap.timeline({ scrollTrigger: { trigger: ".proof-stage", start: "top 76%", end: "top 18%", scrub: 1.05 } })
          .from(".proof-criteria", { x: -64, autoAlpha: 0.22, ease: "power2.out" }, 0)
          .from(".evidence-strip > figure", { y: 68, rotate: (index) => [-2, 1.5, -1, 1.2][index] ?? 0, autoAlpha: 0.2, stagger: 0.08, ease: "power2.out" }, 0.08)
          .from(".client-decision", { x: 64, autoAlpha: 0.22, ease: "power2.out" }, 0.18)
          .from(".criteria-check", { scale: 0, transformOrigin: "center", stagger: 0.05, ease: "back.out(1.4)" }, 0.38)
          .fromTo(".proof-route", { scaleX: 0, transformOrigin: "left center" }, { scaleX: 1, ease: "none" }, 0.32)
          .fromTo(".proof-arrow", { x: -20, autoAlpha: 0 }, { x: 0, autoAlpha: 1, ease: "none" }, 0.42)
          .to(".evidence-strip", { x: -24, ease: "none" }, 0.45);

        gsap.timeline({ scrollTrigger: { trigger: "#about", start: "top 78%", end: "top 22%", scrub: 1 } })
          .from(".production-node", { y: 54, autoAlpha: 0.22, stagger: 0.12, ease: "power2.out" })
          .from(".technology-line", { scaleX: 0, transformOrigin: "center", ease: "power2.inOut" }, 0.35)
          .from(".closing-cta", { y: 42, clipPath: "inset(0 0 100% 0)", ease: "power2.out" }, 0.46);
      });

      mm.add("(max-width: 1023px)", () => {
        ScrollTrigger.batch(".scene-two-source, .process-panel, .decision-paper-wrap, .evidence-strip > figure, .production-node", {
          start: "top 88%",
          once: true,
          interval: 0.08,
          batchMax: 3,
          onEnter: (batch) => gsap.from(batch, { y: 34, autoAlpha: 0, duration: 0.72, stagger: 0.065, ease: premiumEase, clearProps: "transform,opacity,visibility" }),
        });

        gsap.utils.toArray<HTMLElement>(".mobile-flow-line").forEach((line) => {
          gsap.fromTo(line, { scaleY: 0, transformOrigin: "top center" }, { scaleY: 1, ease: "none", scrollTrigger: { trigger: line, start: "top 88%", end: "bottom 62%", scrub: 0.55 } });
        });
      });

      requestAnimationFrame(() => ScrollTrigger.refresh());

      return () => mm.revert();
    },
    { scope: root },
  );

  return (
    <main ref={root} className="paper-texture landing-canvas min-h-[100dvh] overflow-x-clip">
      <div className="pointer-events-none fixed left-0 top-0 z-50 hidden h-dvh w-px bg-[#282923]/10 lg:block" aria-hidden="true"><span className="scroll-progress block h-full w-px origin-top bg-[#a66a00]" /></div>
      <header className="relative z-30 px-5 sm:px-8">
        <div className="site-header-inner mx-auto flex h-[72px] max-w-[1344px] items-center justify-between border-b border-[#a9a69f] sm:h-[78px]">
          <a href="#" className="focus-ring text-[17px] font-semibold tracking-[-0.035em] text-[#171815] sm:text-[18px]">Delividence</a>
          <nav className="absolute left-1/2 hidden -translate-x-1/2 items-center gap-[54px] text-[13px] font-medium text-[#343530] md:flex">
            <a className="focus-ring hover:text-[#11120f]" href="#workflow">Workflow</a>
            <a className="focus-ring hover:text-[#11120f]" href="#review">Review</a>
            <a className="focus-ring hover:text-[#11120f]" href="#about">About</a>
          </nav>
          <div className="flex items-center gap-7">
            <button className="tap focus-ring hidden text-[13px] font-medium text-[#343530] hover:text-[#11120f] sm:inline-flex" onClick={onSignIn}>Sign in</button>
            <button className="tap focus-ring rounded-[4px] bg-[#8d5900] px-3.5 py-2.5 text-[12px] font-semibold text-white shadow-[0_3px_10px_rgba(120,76,0,.16)] hover:bg-[#744900] sm:px-5 sm:py-3 sm:text-[13px]" onClick={onSignIn}>Create a record</button>
          </div>
        </div>
      </header>

      <section className="hero-stage mx-auto grid min-h-[calc(100svh-72px)] max-w-[1344px] items-center gap-12 px-5 py-14 sm:min-h-[calc(100svh-78px)] sm:px-8 lg:grid-cols-[36.5%_63.5%] lg:px-0 lg:py-10">
        <div className="hero-copy relative z-10 self-center lg:pb-3">
          <p className="handwritten max-w-[175px] border-l border-[#c98a17] pl-[14px] text-[21px] font-medium leading-[1.34] text-[#ba7807]">One place for<br />the material<br />behind the work</p>
          <h1 className="mt-10 max-w-[8.8ch] text-[clamp(48px,14vw,80px)] font-medium leading-[1.02] tracking-[-0.058em] text-[#171815] sm:mt-[46px]">The brief is<br />more than<br />the brief.</h1>
          <p className="mt-6 max-w-[425px] text-[16px] leading-[1.65] tracking-[-0.015em] text-[#595a55] sm:mt-7 sm:text-[17px]">Emails, notes, images, and calls become a record the project can actually use.</p>
          <div className="mt-8 flex flex-wrap items-center gap-7 sm:mt-9 sm:gap-9">
            <button className="tap focus-ring rounded-[4px] bg-[#8d5900] px-[22px] py-[14px] text-[14px] font-semibold text-white shadow-[0_3px_10px_rgba(120,76,0,.16)] hover:bg-[#744900]" onClick={onSignIn}>Create a record</button>
            <button className="tap focus-ring inline-flex items-center border-b border-[#292a26] pb-[3px] text-[14px] font-semibold text-[#292a26]" onClick={() => { onSample(); document.getElementById("workflow")?.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }); }}>See a sample</button>
          </div>
          {error && <p className="mt-5 max-w-xl border border-[var(--danger)]/20 bg-white/35 p-3 text-sm text-[var(--danger)]">{error}</p>}
        </div>
        <HeroArtifacts />
      </section>

      <section id="workflow" className="material-stage editorial-section relative mx-auto max-w-[1344px] scroll-mt-20 px-5 py-20 sm:px-8 sm:py-24 lg:px-0 lg:py-28 xl:py-32">
        <SectionHeading number="2" title="Read the material together." />
        <div className="mt-9 border-y border-[#c9c5bc] lg:mt-12 lg:grid lg:grid-cols-[72%_28%]">
          <div className="border-[#c9c5bc] py-5 lg:border-r lg:px-5 lg:py-6">
            <div className="flex items-center gap-5"><p className="mono shrink-0 text-[10px] font-semibold tracking-[0.08em]">SOURCES</p><span className="source-progress h-px flex-1 bg-[#565750]" /><ChevronRight className="source-arrow" size={18} strokeWidth={1.25} /></div>
            <div className="editorial-scroll -mx-5 mt-6 flex snap-x snap-mandatory gap-3 overflow-x-auto px-5 pb-4 sm:-mx-8 sm:px-8 lg:mx-0 lg:grid lg:grid-cols-5 lg:gap-4 lg:overflow-visible lg:px-0 lg:pb-0">
              <MaterialSourceCard kind="brief" label="BRIEF" caption="What was said." /><MaterialSourceCard kind="email" label="EMAIL" caption="What was said." /><MaterialSourceCard kind="call" label="CALL" caption="What was said." /><MaterialSourceCard kind="screenshot" label="SCREENSHOT" caption="What was shown." /><MaterialSourceCard kind="video" label="VIDEO" caption="What was shown." />
            </div>
          </div>
          <div className="project-record-panel relative py-6 lg:p-6">
            <span className="project-record-bracket absolute right-1 top-[29%] h-[62%] w-3 border-y border-r border-[#c98a17] lg:right-5" aria-hidden="true" />
            <p className="mono text-[10px] font-semibold tracking-[0.08em]">PROJECT RECORD</p>
            <h3 className="mt-7 text-[18px] font-semibold tracking-[-0.025em]">Project Agreement (v1)</h3>
            <ul className="mt-6 space-y-4 pr-7 text-[14px] leading-6 text-[#3f403b]">{agreementItems.map((item) => <li key={item}>{item}</li>)}</ul>
            <p className="mono mt-7 text-[11px] text-[#555650]">Date: Apr 29 · Owner: Design Team</p>
          </div>
        </div>
        <JourneyConnector label="Record assembled" />
      </section>

      <section id="clarification" className="editorial-section relative mx-auto max-w-[1344px] scroll-mt-20 px-5 py-20 sm:px-8 sm:py-24 lg:px-0 lg:py-28 xl:py-32">
        <SectionHeading number="3" title="Ask only what the record cannot answer." />
        <div className="relative mt-9 lg:mt-12 lg:grid lg:grid-cols-[22%_28%_25%_25%]">
          <SourceListPanel /><MobileFlow /><ExtractedPlanPanel /><MobileFlow /><QuestionsPanel /><MobileFlow /><ClientReviewPanel />
          <span className="client-handoff-arrow pointer-events-none absolute left-[73.5%] top-[48%] z-20 hidden h-px w-[3%] bg-[#c98a17] lg:block" aria-hidden="true"><ChevronRight className="absolute -right-2.5 -top-2.5 text-[#b57900]" size={20} strokeWidth={1.4} /></span>
        </div>
        <JourneyConnector label="Questions resolved" />
      </section>

      <section id="changes" className="decision-stage editorial-section relative mx-auto max-w-[1344px] scroll-mt-20 px-5 py-20 sm:px-8 sm:py-24 lg:px-0 lg:py-28 xl:py-32">
        <SectionHeading number="4" title="Keep old decisions intact." />
        <div className="relative mt-10 lg:mt-12">
          <span className="decision-route absolute left-[7%] right-[7%] top-[25px] hidden h-px bg-[#c98a17] lg:block" aria-hidden="true" />
          <ChevronRight className="decision-arrow absolute left-[7%] top-[15px] z-20 hidden bg-[#f4f1ea] text-[#b57900] lg:block" size={20} strokeWidth={1.4} aria-hidden="true" />
          <div className="decision-timeline relative grid gap-9 lg:grid-cols-3 lg:gap-4">
            <DecisionPaper eyebrow="BASELINE AGREEMENT (v1) · Apr 29" variant="ruled"><p className="handwritten text-[27px] leading-[1.55]">Project Agreement (v1)<br />- Simplify the header and reduce copy.<br />- Start the hero video muted.<br />- Button label: “Get in touch”.<br />- Maintain clean layout and lighter headline weight.<br /><br />Owner: Design Team</p></DecisionPaper>
            <DecisionPaper eyebrow="FIELD NOTE (NEW REQUEST) · May 1" variant="grid"><p className="handwritten text-[27px] leading-[1.55]"><u>Field Note</u><br />Request from Sarah (email):<br />Add testimonials section below the hero.<br /><br />Keep the tone consistent.<br /><br />See email_sarah_0501.eml (S-06)</p></DecisionPaper>
            <DecisionPaper eyebrow="CHANGE DECISION · May 1" variant="decision"><span className="absolute right-5 top-[25%] h-[62%] w-3 border-y border-r border-[#c98a17]" aria-hidden="true" /><p className="mono text-[17px] leading-[1.65]"><u>Change Decision (D-01)</u><br /><br /><b>Decision:</b> Add testimonials section below the hero.<br /><br /><b>Rationale:</b> Supports trust signal without impacting core message.<br /><br /><b>Impact:</b> Affects layout below the fold; no change to hero.<br /><b>Approved by:</b> Sarah Park<br /><b>Date:</b> May 1</p></DecisionPaper>
          </div>
        </div>
        <p className="mt-7 max-w-5xl text-[14px] leading-6 text-[#565750] sm:text-[15px]">New requests are captured as field notes and resolved as formal change decisions—without editing the original agreement.</p>
        <JourneyConnector label="Change recorded" />
      </section>

      <section id="review" className="proof-stage editorial-section relative mx-auto max-w-[1344px] scroll-mt-20 px-5 py-20 sm:px-8 sm:py-24 lg:px-0 lg:py-28 xl:py-32">
        <SectionHeading number="5" title="Review what was delivered." />
        <div className="mt-9 border-y border-[#c9c5bc] lg:mt-12 lg:grid lg:grid-cols-[23%_53%_24%]"><ProofCriteria /><EvidencePanel /><ClientDecisionPanel /></div>
        <p className="mt-3 text-[13px] text-[#666760]">Visual feedback is assistive, acceptance remains with the client.</p>
        <JourneyConnector label="Proof reviewed" />
      </section>

      <section id="about" className="editorial-section relative mx-auto max-w-[1344px] scroll-mt-20 px-5 pb-20 pt-20 sm:px-8 sm:pb-24 sm:pt-24 lg:px-0 lg:pb-28 lg:pt-28 xl:pt-32">
        <SectionHeading number="6" title="Built for production." />
        <div className="mt-9 border-y border-[#bcb8af] lg:mt-7 lg:grid lg:grid-cols-3">
          {[["Source-linked extraction", "Every point in the record links back to what was said or shown."], ["Resumable workflow", "Pause, return, and continue without losing context."], ["Versioned activity record", "Every change, decision, and handoff is recorded with time and author."]].map(([title, body], index) => <article key={title} className="production-node grid grid-cols-[48px_1fr] gap-4 border-b border-[#c9c5bc] py-7 last:border-b-0 lg:block lg:border-b-0 lg:border-r lg:px-8 lg:text-center lg:last:border-r-0"><span className="flex h-10 w-10 items-center justify-center rounded-full border border-[#292a26] text-[16px] lg:hidden">{index + 1}</span><div><h3 className="text-[17px] font-semibold tracking-[-0.02em]">{title}</h3><p className="mt-2 max-w-sm text-[14px] leading-6 text-[#5d5e58] lg:mx-auto">{body}</p></div></article>)}
        </div>
        <p className="technology-line border-b border-[#bcb8af] py-4 text-center text-[13px] text-[#666760]">Gemini 3.5, Google ADK, and Google Cloud are used behind these steps.</p>
        <div className="closing-cta mx-auto mt-20 max-w-3xl text-center sm:mt-24"><h2 className="text-[clamp(34px,5vw,48px)] font-medium leading-[1.12] tracking-[-0.045em]">Give the work a record worth returning to.</h2><button className="tap focus-ring mt-8 min-h-12 w-full rounded-[4px] bg-[#8d5900] px-8 py-3.5 text-[14px] font-semibold text-white shadow-[0_3px_10px_rgba(120,76,0,.16)] hover:bg-[#744900] sm:w-auto" onClick={onSignIn}>Create a record</button></div>
      </section>

      <footer className="border-t border-[#bcb8af] px-5 py-8 sm:px-8"><div className="mx-auto grid max-w-[1344px] gap-6 text-[13px] text-[#5f605a] md:grid-cols-3 md:items-center"><span>© 2026 Delividence</span><nav aria-label="Legal" className="flex flex-wrap gap-x-8 gap-y-3 md:justify-center"><a className="focus-ring hover:text-[#171815]" href="#">Security</a><a className="focus-ring hover:text-[#171815]" href="#">Privacy</a><a className="focus-ring hover:text-[#171815]" href="#">Terms</a></nav><a className="focus-ring hover:text-[#171815] md:text-right" href="mailto:hello@delividence.com">hello@delividence.com</a></div></footer>
    </main>
  );
}

function SectionHeading({ number, title }: { number: string; title: string }) { return <div className="section-heading relative flex items-start gap-4 pb-4 sm:gap-6"><span className="section-number text-[22px] font-medium leading-none sm:text-[24px]">{number}.</span><h2 className="section-title text-[clamp(26px,3vw,36px)] font-medium leading-[1.05] tracking-[-0.04em]">{title}</h2><span className="section-heading-rule absolute inset-x-0 bottom-0 h-px bg-[#bcb8af]" aria-hidden="true" /></div>; }

function JourneyConnector({ label }: { label: string }) {
  return <div className="journey-connector pointer-events-none absolute -bottom-14 left-1/2 z-20 h-28 w-44 -translate-x-1/2" aria-hidden="true"><span className="absolute left-1/2 top-0 h-[86px] w-px bg-[#2f302b]/15" /><span className="journey-progress absolute left-1/2 top-0 h-[86px] w-px origin-top bg-[#c98a17]" /><ArrowDown className="journey-arrow absolute left-1/2 top-0 -translate-x-1/2 bg-[#f4f1ea] text-[#b57900]" size={20} strokeWidth={1.35} /><span className="journey-label mono absolute left-[calc(50%+20px)] top-[43px] hidden whitespace-nowrap text-[9px] uppercase tracking-[0.08em] text-[#77786f] sm:block">{label}</span></div>;
}

function HeroArtifacts() {
  return <div className="hero-art-board w-full">
    <div className="grid grid-cols-2 gap-3 lg:hidden">
      <article className="hero-artifact hero-document col-span-2 p-4"><p className="mono text-[9px]">EMAIL · From: Sarah Park</p><p className="mono mt-4 text-[10px] leading-5">Hi team,<br /><br />Let&apos;s keep the layout clean and the headline weight lighter. Also, the hero video should start muted.<br /><br />— Sarah</p></article>
      <article className="hero-artifact hero-document p-3"><p className="mono text-[8px]">HERO v2</p><p className="mt-4 text-[20px] font-semibold leading-[1.05] tracking-[-0.04em]">Work that<br />moves people.</p><p className="mt-3 text-[9px] leading-4">Strategy, design, and brand craftsmanship.</p></article>
      <article className="hero-artifact hero-document relative min-h-44 overflow-hidden"><Image src="/assets/hero-coast.png" alt="Muted rocky coastline and ocean" fill sizes="45vw" className="object-cover" /><span className="absolute left-1/2 top-1/2 flex h-9 w-9 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-[#f7f4ed]/90"><Play size={14} fill="currentColor" /></span></article>
      <article className="hero-artifact hero-document col-span-2 p-4"><p className="mono text-[9px]">SOURCE INDEX</p><div className="mono mt-3 grid grid-cols-[38px_1fr_auto] gap-y-2 text-[8px]">{[["S-01", "email_sarah_0429.eml", "9:14"], ["S-02", "call_0429.mp3", "10:02"], ["S-03", "hero_v2.png", "10:11"]].map((row) => row.map((cell) => <span key={`${row[0]}-${cell}`} className="truncate">{cell}</span>))}</div></article>
    </div>
    <div className="relative hidden min-h-[570px] w-full lg:block">
      <Image src="/assets/hero-paperclip-raster.png" alt="" aria-hidden="true" width={1024} height={1536} className="hero-artifact pointer-events-none absolute right-[2.5%] top-[-36px] z-20 h-[132px] w-auto object-contain" />
      <Image src="/assets/hero-pencil-raster.png" alt="" aria-hidden="true" width={1024} height={1536} className="hero-artifact pointer-events-none absolute bottom-[-55px] right-[-52px] z-20 h-[440px] w-auto object-contain drop-shadow-[0_16px_10px_rgba(32,33,31,.13)]" />
      <article className="hero-artifact hero-document absolute left-[5%] top-[-12px] h-[280px] w-[39.5%] rotate-[-0.35deg] px-[24px] py-[19px]"><div className="mono flex items-center gap-3 text-[9px] font-medium text-[#3f403b]"><span>EMAIL</span><span>·</span><span>From: Sarah Park</span></div><div className="mono mt-5 text-[10px] leading-[1.55] text-[#242520]"><p>To: Design Team</p><p>Mon, Apr 29, 9:14 AM</p><p className="mt-5">Hi team,</p><p className="mt-3">Let&apos;s keep the layout clean and the<br />headline weight lighter. See the<br />reference below.</p><p className="mt-3">Also, the hero video should start muted.</p><p className="mt-4">— Sarah</p></div></article>
      <article className="hero-artifact hero-document absolute left-[47%] top-[-6px] h-[280px] w-[43.5%] rotate-[0.35deg] px-[24px] py-[19px]"><div className="mono flex items-center gap-3 text-[9px] font-medium text-[#3f403b]"><span>CALL TRANSCRIPT</span><span>·</span><span>04/29 10:02 AM</span></div><div className="mono mt-5 grid grid-cols-[48px_1fr] gap-x-2 gap-y-2 text-[9.5px] leading-[1.38] text-[#242520]"><b className="font-medium">Sarah:</b><span>We should simplify the header.</span><b className="font-medium">James:</b><span>Agreed. Also, reduce the copy.</span><b className="font-medium">Sarah:</b><span>Let&apos;s start the video muted.</span><b className="font-medium">James:</b><span>Noted.</span><b className="font-medium">Sarah:</b><span>And the button label—<br />try “Get in touch”.</span></div><Image src="/assets/waveform-sample.svg" alt="" aria-hidden="true" width={320} height={52} className="mt-[18px] h-[35px] w-full opacity-85" /><p className="mono mt-1 text-[9px] text-[#555650]">07:34 / 32:11</p></article>
      <article className="hero-artifact hero-document absolute left-[3.5%] top-[292px] h-[245px] w-[47%] rotate-[0.3deg] overflow-hidden"><div className="mono border-b border-[#d7d2c9] px-[22px] py-[12px] text-[9px] text-[#4e4f49]">HERO v2&nbsp;&nbsp; · &nbsp;&nbsp;design-system.pdf</div><div className="grid h-[202px] grid-cols-[48%_52%]"><div className="px-[23px] py-[20px]"><p className="text-[27px] font-semibold leading-[1.05] tracking-[-0.045em] text-[#181915]">Work that<br />moves people.</p><p className="mt-5 text-[10px] leading-[1.45] text-[#343530]">Strategy, design, and<br />brand craftsmanship.</p><span className="mt-6 inline-flex rounded-[2px] bg-[#151612] px-3 py-2 text-[9px] font-medium text-white">Get in touch</span></div><div className="relative m-[12px] ml-0 overflow-hidden rounded-[2px]"><Image src="/assets/hero-coast.png" alt="Muted rocky coastline and ocean" fill sizes="220px" className="object-cover" /><span className="absolute left-1/2 top-1/2 flex h-8 w-8 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-[#f7f4ed]/90 text-[#20211d] shadow-sm"><Play size={13} fill="currentColor" /></span></div></div></article>
      <article className="hero-artifact hero-document absolute left-[53%] top-[306px] h-[238px] w-[38.5%] rotate-[-0.25deg] px-[22px] py-[17px]"><p className="mono text-[9px] font-medium text-[#4a4b45]">SOURCE INDEX</p><table className="mono mt-[18px] w-full table-fixed text-left text-[8.5px] leading-5 text-[#393a35]"><thead className="text-[7.5px] font-normal text-[#696a63]"><tr><th scope="col" className="w-[16%] font-normal">ID</th><th scope="col" className="w-[23%] font-normal">TYPE</th><th scope="col" className="w-[41%] font-normal">FILE / LINK</th><th scope="col" className="w-[20%] font-normal">ADDED</th></tr></thead><tbody>{[["S-01", "Email", "email_sarah_0429.eml", "9:14 AM"], ["S-02", "Call", "call_0429.mp3", "10:02 AM"], ["S-03", "Screenshot", "hero_v2.png", "10:11 AM"], ["S-04", "Brief", "brief_project.pdf", "Apr 28"], ["S-05", "Video ref", "hero_ref.mp4", "Apr 27"]].map(([id, type, file, added]) => <tr key={id}><td className="pt-[9px] underline">{id}</td><td className="pt-[9px]">{type}</td><td className="truncate pt-[9px] underline">{file}</td><td className="pt-[9px]">{added}</td></tr>)}</tbody></table></article>
      <HeroIndexMarker label="S-01" className="left-[-1.5%] top-[112px]" /><HeroIndexMarker label="S-02" className="left-[-2.5%] top-[374px]" /><HeroIndexMarker label="S-03" className="right-[4.5%] top-[386px]" />
    </div>
  </div>;
}

function HeroIndexMarker({ label, className }: { label: string; className: string }) { return <span aria-hidden="true" className={`hero-artifact absolute h-[72px] w-[18px] border-y border-l border-[#c98a17] text-[#b67608] ${className}`}><span className="mono absolute left-[12px] top-1/2 w-max -translate-y-1/2 rotate-90 whitespace-nowrap text-[9px]">{label}</span></span>; }

function MaterialSourceCard({ kind, label, caption }: { kind: "brief" | "email" | "call" | "screenshot" | "video"; label: string; caption: string }) {
  return <article className="scene-two-source reveal-item w-[172px] shrink-0 snap-start lg:w-auto"><p className="mono mb-3 text-[10px] font-semibold tracking-[0.08em]">{label}</p><div className="hero-document relative h-[260px] overflow-hidden p-4 lg:h-[238px] lg:p-3">
    {kind === "brief" && <><p className="mono text-[7px] font-semibold">Project Notes</p><div className="mt-4 space-y-1.5">{Array.from({ length: 13 }).map((_, i) => <span key={i} className="block h-px bg-[#77786f]/35" style={{ width: `${70 + (i % 4) * 8}%` }} />)}</div><FileText className="absolute bottom-4 left-4" size={13} strokeWidth={1.4} /></>}
    {kind === "email" && <div className="mono text-[8px] leading-[1.7]"><p>From: Sarah Park</p><p>To: Design Team</p><p>Mon, Apr 29, 9:14 AM</p><p className="mt-4">Hi team,</p><p className="mt-3">Let&apos;s keep the layout clean and the headline weight lighter.</p><p className="mt-3">Also, the hero video should start muted.</p><p className="mt-3">— Sarah</p></div>}
    {kind === "call" && <div className="mono text-[8px] leading-[1.8]"><p><b>James:</b> Let&apos;s tighten the headline.</p><p className="mt-3"><b>Sarah:</b> Yes, and start the video muted.</p><p className="mt-3"><b>James:</b> Noted.</p><Image src="/assets/waveform-sample.svg" alt="" width={180} height={40} className="absolute bottom-7 left-3 right-3 h-auto w-[calc(100%-24px)]" /><span className="absolute bottom-2 right-3">15:42</span></div>}
    {kind === "screenshot" && <div><h3 className="text-[18px] font-semibold leading-[1.05] tracking-[-0.035em]">Work that<br />moves people.</h3><p className="mt-4 text-[8px] leading-4">Strategy, design, and brand craftsmanship.</p><span className="mt-4 inline-flex bg-[#171815] px-2 py-1.5 text-[7px] text-white">Get in touch</span><div className="absolute bottom-3 left-3 right-3 h-[92px] overflow-hidden"><Image src="/assets/hero-coast.png" alt="Coastline reference" fill sizes="150px" className="object-cover" /><Play className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-white" size={18} fill="currentColor" /></div></div>}
    {kind === "video" && <><Image src="/assets/hero-coast.png" alt="Coastline video reference" fill sizes="180px" className="object-cover" /><span className="absolute left-1/2 top-1/2 flex h-10 w-10 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-white/85"><Play size={16} fill="currentColor" /></span><span className="mono absolute bottom-3 right-3 text-[9px] text-white">00:18</span></>}
  </div><p className="mt-3 text-[12px] text-[#555650]">{caption}</p></article>;
}

function Panel({ children, className = "" }: { children: React.ReactNode; className?: string }) { return <article className={`process-panel border border-[#c9c5bc] bg-[#f8f5ef]/35 lg:border-r-0 lg:last:border-r ${className}`}>{children}</article>; }
function PanelHeader({ children }: { children: React.ReactNode }) { return <div className="flex min-h-12 items-center justify-between border-b border-[#d4d0c7] px-4"><p className="mono text-[10px] font-semibold tracking-[0.08em]">{children}</p><span className="hidden text-[16px] lg:block">⌃</span></div>; }

function SourceListPanel() { return <Panel><PanelHeader>SOURCES</PanelHeader><div>{sourceFiles.map(([name, time, kind]) => { const Icon = kind === "mail" ? Mail : kind === "audio" ? AudioLines : kind === "image" ? ImageIcon : kind === "video" ? Video : FileText; return <div key={name} className="grid min-h-[66px] grid-cols-[32px_1fr_20px] items-center gap-3 border-b border-[#dedad1] px-4"><span className="flex h-8 w-8 items-center justify-center bg-[#e9e6df]"><Icon size={15} strokeWidth={1.5} /></span><div className="min-w-0"><p className="truncate text-[12px]">{name}</p><p className="mt-1 text-[10px] text-[#6b6c65]">{time}</p></div><ChevronRight size={15} className="lg:hidden" /></div>; })}<button className="tap focus-ring flex min-h-12 w-full items-center gap-3 px-4 text-[12px]"><Plus size={16} /> Add source</button></div></Panel>; }

function ExtractedPlanPanel() { return <Panel><PanelHeader>EXTRACTED PLAN</PanelHeader><div className="px-5 py-5"><h3 className="text-[15px] font-semibold">Project Agreement (v1)</h3><ul className="mt-5 space-y-3 text-[13px] leading-5 text-[#3f403b]">{agreementItems.map((item) => <li key={item}>{item}</li>)}</ul><p className="mono mt-6 text-[10px] text-[#77786f]">Last updated: Apr 29, 10:11 AM</p></div><div className="border-t border-[#d4d0c7] px-5 py-4"><p className="mono text-[10px] font-semibold">LINKED EVIDENCE</p><div className="mt-3 flex flex-wrap gap-2">{[1, 2, 3, 4, 5].map((n) => <span key={n} className="border border-[#bdb9b0] px-3 py-1.5 text-[10px]">S-0{n}</span>)}</div><a href="#workflow" className="focus-ring mt-4 inline-block border-b border-[#292a26] text-[11px]">View all sources</a></div></Panel>; }

function QuestionsPanel() { const questions = ["What is the final duration for the hero video?", "Should the button have a secondary style?", "Do we need a mobile specific layout?"]; return <Panel><PanelHeader>UNRESOLVED QUESTIONS</PanelHeader><div className="space-y-3 p-4">{questions.map((q, i) => <button key={q} className="tap focus-ring grid min-h-[76px] w-full grid-cols-[24px_1fr_18px] items-start gap-2 border border-[#d4d0c7] p-4 text-left text-[12px] leading-5"><b>{i + 1}</b><span>{q}</span><ChevronRight size={16} className="lg:hidden" /></button>)}</div></Panel>; }

function ClientReviewPanel() { return <Panel><PanelHeader>CLIENT REVIEW</PanelHeader><div className="p-4"><label className="text-[11px] text-[#666760]" htmlFor="review-link">Secure review link</label><div className="mt-2 flex h-10 items-center border border-[#aaa69d] px-3"><input id="review-link" readOnly value="delividence.com/r/8f3k2a" className="min-w-0 flex-1 bg-transparent text-[12px] outline-none" /><Copy size={14} /></div><p className="mono mt-6 text-[10px] text-[#666760]">Client reply · May 1, 11:08 AM</p><ol className="mt-4 space-y-3 text-[12px] leading-5"><li><b className="mr-4">1</b>20 seconds.</li><li><b className="mr-4">2</b>Yes, outline style.</li><li className="flex"><b className="mr-4">3</b><span>Yes, mobile layout is required.</span></li></ol></div><div className="flex items-center gap-3 border-t border-[#d4d0c7] px-4 py-4 text-[11px]"><Check size={15} strokeWidth={1.5} /><span>Plan updated<br /><span className="text-[#77786f]">May 1, 11:09 AM</span></span></div></Panel>; }

function MobileFlow() { return <div className="mobile-flow-line relative mx-auto h-16 w-px bg-[#c98a17] lg:hidden"><ArrowDown className="absolute -bottom-1 left-1/2 -translate-x-1/2 text-[#c98a17]" size={20} strokeWidth={1.5} /></div>; }
function DecisionPaper({ eyebrow, variant, children }: { eyebrow: string; variant: "ruled" | "grid" | "decision"; children: React.ReactNode }) { return <article className="decision-paper-wrap relative"><p className="mono mb-4 text-[10px] font-semibold tracking-[0.06em]">{eyebrow}</p><div className={`decision-paper paper-card relative min-h-[390px] p-6 sm:p-8 ${variant === "ruled" ? "paper-ruled" : variant === "grid" ? "paper-grid" : "paper-decision"}`}>{children}</div></article>; }

function ProofCriteria() { const criteria = ["Header simplification", "Video starts muted", "Button label", "Testimonials section", "Mobile layout"]; return <article className="proof-criteria border-[#c9c5bc] py-5 lg:border-r lg:p-5"><p className="mono text-[10px] font-semibold">PROOF: Homepage v2</p><p className="mt-1 text-[10px] text-[#77786f]">Delivered: May 5, 4:42 PM</p><div className="mt-5 grid grid-cols-[1fr_auto] border-y border-[#d4d0c7] py-3 text-[10px] text-[#77786f]"><span>Criterion</span><span>Status</span></div><div>{criteria.map((criterion) => <div key={criterion} className="grid min-h-10 grid-cols-[1fr_auto] items-center text-[11px]"><span>{criterion}</span><span className="criteria-check flex items-center gap-1.5 text-[#2d7552]"><Check size={13} /> Met</span></div>)}</div></article>; }

function EvidencePanel() { return <article className="evidence-panel min-w-0 border-[#c9c5bc] py-5 lg:border-r lg:p-5"><div className="flex items-center gap-4"><p className="mono shrink-0 text-[10px] font-semibold">EVIDENCE</p><span className="proof-route h-px flex-1 bg-[#c98a17]" aria-hidden="true" /><ChevronRight className="proof-arrow text-[#b57900]" size={17} strokeWidth={1.4} aria-hidden="true" /></div><div className="editorial-scroll -mx-5 mt-5 overflow-x-auto px-5 pb-3 lg:mx-0 lg:px-0"><div className="evidence-strip flex w-max gap-3"><EvidenceCard type="screen" file="hero_v2_final.png" /><EvidenceCard type="video" file="hero_v2_final.mp4" /><EvidenceCard type="mobile" file="mobile_v2.png" /><EvidenceCard type="note" file="testimonials_v2.png" /></div></div><div className="mt-4 border-t border-[#d4d0c7] pt-4"><p className="mono text-[9px] font-semibold">LIVE URL</p><a href="https://deliv.co" className="focus-ring mt-1 inline-flex items-center gap-2 border-b border-[#292a26] text-[12px]">https://deliv.co/ <ExternalLink size={13} /></a></div></article>; }

function EvidenceCard({ type, file }: { type: "screen" | "video" | "mobile" | "note"; file: string }) { return <figure className="w-[142px] shrink-0 snap-start"><div className="hero-document relative h-[154px] overflow-hidden p-3">{type === "screen" && <><p className="text-[15px] font-semibold leading-none">Work that<br />moves people.</p><p className="mt-3 text-[7px]">Strategy, design, and brand craftsmanship.</p><div className="absolute bottom-2 left-2 right-2 h-[66px] overflow-hidden"><Image src="/assets/hero-coast.png" alt="Final homepage screenshot" fill sizes="130px" className="object-cover" /></div></>}{type === "video" && <><Image src="/assets/hero-coast.png" alt="Final homepage video" fill sizes="142px" className="object-cover" /><Play className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-white" fill="currentColor" /><span className="absolute bottom-2 right-2 text-[9px] text-white">00:20</span></>}{type === "mobile" && <div className="mx-auto h-full w-[66px] rounded-[12px] border-[3px] border-[#1d1e1b] bg-[#f4f1ea] p-1"><div className="h-2 border-b border-[#bbb7ae]" /><p className="mt-2 text-[7px] font-bold">Work that<br />moves people.</p><div className="relative mt-2 h-16 overflow-hidden"><Image src="/assets/hero-coast.png" alt="Mobile capture" fill sizes="60px" className="object-cover" /></div></div>}{type === "note" && <><p className="mono text-center text-[8px]">Client note</p><div className="mt-5 space-y-5">{[1, 2].map((n) => <div key={n} className="flex gap-2"><span className="h-5 w-5 rounded-full bg-[#d6d2c9]" /><div className="flex-1 space-y-1"><span className="block h-px bg-[#77786f]/50" /><span className="block h-px w-4/5 bg-[#77786f]/35" /><span className="block h-px w-3/5 bg-[#77786f]/35" /></div></div>)}</div></>}</div><figcaption className="mono mt-2 truncate text-[9px] text-[#666760]">{file}</figcaption></figure>; }

function ClientDecisionPanel() { return <article className="client-decision py-5 lg:p-5"><p className="mono text-[10px] font-semibold">CLIENT DECISION</p><p className="mt-6 text-[12px]">This delivers what was agreed.</p><div className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-1"><button className="tap focus-ring flex min-h-11 items-center justify-center gap-2 border border-[#2d7552] text-[12px] text-[#2d7552]"><Check size={14} /> Accept</button><button className="tap focus-ring min-h-11 border border-[#aaa69d] text-[12px]">Request changes</button><button className="tap focus-ring min-h-11 border border-[#aaa69d] text-[12px] sm:col-span-2 lg:col-span-1">Not accept</button></div><label htmlFor="review-comment" className="mt-6 block text-[10px] text-[#77786f]">Add comment (optional)</label><textarea id="review-comment" className="mt-2 min-h-24 w-full resize-none border border-[#c9c5bc] bg-transparent p-3 text-[12px] outline-none focus:border-[#b57900]" /></article>; }
