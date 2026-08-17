"use client";

import Link from "next/link";
import {
  ArrowRight,
  ShieldCheck,
  Activity,
  FileCheck2,
  LockKeyhole,
  Zap,
  CheckCircle2,
  Terminal,
  Network,
  Cpu,
  Radar,
} from "lucide-react";

export default function Home() {
  return (
    <main className="cyber-home relative min-h-screen overflow-hidden bg-[#050504] text-white">
      {/* =========================================================
          BACKGROUND
      ========================================================= */}

      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        {/* Orange glow */}
        <div className="absolute left-[8%] top-[28%] h-[450px] w-[450px] rounded-full bg-orange-600/10 blur-[150px]" />

        {/* Green glow */}
        <div className="absolute right-[8%] top-[35%] h-[400px] w-[400px] rounded-full bg-emerald-500/5 blur-[150px]" />

        {/* Grid */}
        <div className="cyber-grid absolute inset-0 opacity-40" />

        {/* Stars / particles */}
        <CyberParticles />

        {/* Scan line */}
        <div className="scan-line absolute left-0 top-0 h-px w-full bg-gradient-to-r from-transparent via-orange-500/60 to-transparent" />
      </div>

      {/* =========================================================
          NAVIGATION
      ========================================================= */}

      <header className="relative z-50 border-b border-orange-500/10 bg-[#050504]/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-[1500px] items-center justify-between px-5 sm:px-8">
          {/* Logo */}
          <Link href="/" className="group flex items-center gap-3">
            <div className="relative flex h-9 w-9 items-center justify-center border border-orange-500/50 bg-orange-500/5">
              <div className="absolute inset-1 border border-emerald-400/30" />
              <ShieldCheck
                size={18}
                className="text-orange-400 transition group-hover:text-emerald-400"
              />
            </div>

            <div>
              <div className="font-mono text-lg font-bold tracking-[0.28em]">
                CYGRC
              </div>

              <div className="font-mono text-[8px] tracking-[0.22em] text-zinc-600">
                SECURITY ECOSYSTEM
              </div>
            </div>
          </Link>

          {/* Center navigation */}
          <nav className="hidden items-center gap-8 lg:flex">
            <CyberNavLink href="#platform" text="PLATFORM" />
            <CyberNavLink href="#features" text="CAPABILITIES" />
            <CyberNavLink href="#security" text="SECURITY" />
            <CyberNavLink href="#system" text="SYSTEM" />
          </nav>

          {/* Right */}
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 font-mono text-[9px] tracking-widest text-zinc-600 sm:flex">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
              SYSTEM ONLINE
            </div>

            <Link
              href="/login"
              className="border border-orange-500/30 px-4 py-2 font-mono text-[10px] font-bold tracking-widest text-orange-400 transition hover:border-orange-400 hover:bg-orange-500/10"
            >
              LOGIN
            </Link>
          </div>
        </div>
      </header>

      {/* =========================================================
          HERO
      ========================================================= */}

      <section
        id="platform"
        className="relative z-10 flex min-h-[calc(100vh-64px)] items-center justify-center px-5 py-20 sm:px-8"
      >
        {/* Technical corner labels */}
        <div className="absolute left-5 top-8 hidden font-mono text-[9px] leading-5 tracking-[0.2em] text-zinc-700 md:block">
          <div>SYS_CORE: CYGRC</div>
          <div>NETWORK: ENCRYPTED</div>
          <div>STATUS: <span className="text-emerald-500">ACTIVE</span></div>
        </div>

        <div className="absolute right-5 top-8 hidden text-right font-mono text-[9px] leading-5 tracking-[0.2em] text-zinc-700 md:block">
          <div>BROWSER: SECURE</div>
          <div>
            SIGNAL: <span className="text-orange-500">STRONG</span>
          </div>
          <div>PROTOCOL: GRC-01</div>
        </div>

        {/* Main content */}
        <div className="relative w-full max-w-[1200px] text-center">
          {/* Status */}
          <div className="mb-8 flex items-center justify-center gap-3 font-mono text-[10px] tracking-[0.3em] text-orange-500">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-orange-500 shadow-[0_0_12px_#f97316]" />
            SYSTEM_PROTOCOL_HARDENED
          </div>

          {/* Decorative brackets */}
          <div className="absolute left-[8%] top-[10%] hidden h-8 w-8 border-l border-t border-orange-600/40 md:block" />
          <div className="absolute right-[8%] top-[10%] hidden h-8 w-8 border-r border-t border-orange-600/40 md:block" />
          <div className="absolute bottom-[12%] left-[8%] hidden h-8 w-8 border-b border-l border-orange-600/40 md:block" />
          <div className="absolute bottom-[12%] right-[8%] hidden h-8 w-8 border-b border-r border-orange-600/40 md:block" />

          {/* Hero heading */}
          <h1 className="cyber-title mx-auto max-w-5xl font-mono uppercase leading-[0.9]">
            <span className="block text-[clamp(3rem,8vw,8rem)] font-extralight tracking-[-0.07em] text-white">
              SECURING
            </span>

            <span className="cyber-gradient block text-[clamp(3rem,8vw,8rem)] font-extralight tracking-[-0.07em]">
              CYBER SECURITY
            </span>

            <span className="mt-3 block text-[clamp(1.5rem,4vw,3.8rem)] font-extralight tracking-[0.35em] text-zinc-400">
              ECOSYSTEM
              <span className="text-emerald-400">.</span>
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mx-auto mt-10 max-w-2xl font-mono text-xs leading-7 tracking-[0.12em] text-zinc-500 sm:text-sm">
            GOVERNANCE // RISK // COMPLIANCE // AUDITS // CONTROLS
            <br />
            ONE INTELLIGENT PLATFORM FOR CONTINUOUS SECURITY OPERATIONS.
          </p>

          {/* =====================================================
              DATA NETWORK
          ===================================================== */}

          <div className="relative mx-auto mt-16 h-32 max-w-5xl">
            {/* horizontal center line */}
            <div className="absolute left-0 right-0 top-1/2 h-px bg-gradient-to-r from-transparent via-orange-700/40 to-transparent" />

            {/* Network lines */}
            <div className="network-line network-line-1" />
            <div className="network-line network-line-2" />
            <div className="network-line network-line-3" />
            <div className="network-line network-line-4" />
            <div className="network-line network-line-5" />

            {/* Central node */}
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
              <div className="absolute -inset-8 animate-pulse rounded-full bg-orange-500/10 blur-xl" />

              <div className="relative flex h-12 w-12 items-center justify-center rounded-full border-2 border-orange-500 bg-[#050504] shadow-[0_0_30px_rgba(249,115,22,0.5)]">
                <div className="h-2 w-2 rounded-full bg-orange-400 shadow-[0_0_15px_#fb923c]" />
              </div>

              <div className="radar-ring absolute -inset-5 rounded-full border border-orange-500/20" />
            </div>

            {/* Data nodes */}
            <DataNode className="left-[8%] top-[50%]" />
            <DataNode className="left-[18%] top-[36%]" />
            <DataNode className="left-[28%] top-[60%]" />
            <DataNode className="right-[28%] top-[40%]" green />
            <DataNode className="right-[17%] top-[58%]" />
            <DataNode className="right-[7%] top-[50%]" green />
          </div>

          {/* Buttons */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/login"
              className="cyber-button group inline-flex items-center gap-3 bg-orange-500 px-7 py-3.5 font-mono text-xs font-bold tracking-[0.15em] text-black transition hover:bg-orange-400"
            >
              ACCESS CONSOLE
              <ArrowRight
                size={15}
                className="transition-transform group-hover:translate-x-1"
              />
            </Link>

            <Link
              href="/signup"
              className="group inline-flex items-center gap-3 border border-zinc-700 bg-black/40 px-7 py-3.5 font-mono text-xs font-bold tracking-[0.15em] text-zinc-300 transition hover:border-emerald-500/60 hover:text-emerald-400"
            >
              INITIALIZE ACCOUNT
              <span className="text-emerald-500">+</span>
            </Link>
          </div>

          {/* Bottom status */}
          <div className="mt-10 flex flex-wrap justify-center gap-x-8 gap-y-3 font-mono text-[9px] tracking-[0.18em] text-zinc-600">
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              RISK_VISIBILITY
            </span>

            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              AUDIT_READINESS
            </span>

            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              COMPLIANCE_TRACKING
            </span>
          </div>
        </div>
      </section>

      {/* =========================================================
          SYSTEM STATUS
      ========================================================= */}

      <section
        id="system"
        className="relative z-10 border-y border-orange-500/10 bg-black/40 px-5 py-16 sm:px-8"
      >
        <div className="mx-auto max-w-[1200px]">
          <div className="mb-10 flex items-center justify-between">
            <div>
              <p className="font-mono text-[10px] tracking-[0.3em] text-orange-500">
                SYSTEM_STATUS
              </p>
              <h2 className="mt-2 font-mono text-2xl tracking-wider text-white">
                SECURITY OPERATIONS
              </h2>
            </div>

            <div className="hidden font-mono text-[9px] tracking-widest text-zinc-600 sm:block">
              SYS_STABILITY: <span className="text-emerald-500">100%</span>
            </div>
          </div>

          <div className="grid gap-px border border-orange-500/10 bg-orange-500/10 sm:grid-cols-2 lg:grid-cols-4">
            <SystemCard
              icon={<Activity size={18} />}
              label="ACTIVE RISKS"
              value="142"
              status="-8% VS LAST MONTH"
              danger
            />

            <SystemCard
              icon={<ShieldCheck size={18} />}
              label="ACTIVE CONTROLS"
              value="1,204"
              status="+4% VS LAST MONTH"
            />

            <SystemCard
              icon={<FileCheck2 size={18} />}
              label="COMPLIANCE"
              value="87%"
              status="+2% VS LAST MONTH"
            />

            <SystemCard
              icon={<LockKeyhole size={18} />}
              label="EVIDENCE"
              value="4,521"
              status="+12% VS LAST MONTH"
            />
          </div>
        </div>
      </section>

      {/* =========================================================
          FEATURES
      ========================================================= */}

      <section
        id="features"
        className="relative z-10 px-5 py-24 sm:px-8"
      >
        <div className="mx-auto max-w-[1200px]">
          <div className="max-w-2xl">
            <p className="font-mono text-[10px] tracking-[0.3em] text-orange-500">
              CORE_CAPABILITIES
            </p>

            <h2 className="mt-4 font-mono text-3xl uppercase tracking-tight text-white sm:text-5xl">
              One system.
              <br />
              <span className="text-orange-500">Complete visibility.</span>
            </h2>

            <p className="mt-6 max-w-xl font-mono text-xs leading-7 tracking-wide text-zinc-600">
              CYGRC CONNECTS GOVERNANCE, RISK, COMPLIANCE, CONTROLS,
              EVIDENCE, AUDITS AND INCIDENTS INTO ONE CONTINUOUS SECURITY
              OPERATING ENVIRONMENT.
            </p>
          </div>

          <div className="mt-14 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <CyberFeature
              icon={<ShieldCheck size={20} />}
              number="01"
              title="GOVERNANCE"
              text="Manage policies, frameworks, controls and organizational governance."
              href="/compliance"
            />

            <CyberFeature
              icon={<Activity size={20} />}
              number="02"
              title="RISK MANAGEMENT"
              text="Identify, assess, prioritize and continuously monitor security risks."
              href="/risks"
            />

            <CyberFeature
              icon={<FileCheck2 size={20} />}
              number="03"
              title="COMPLIANCE"
              text="Track frameworks, assessments, evidence and compliance posture."
              href="/compliance"
            />

            <CyberFeature
              icon={<Zap size={20} />}
              number="04"
              title="INCIDENT RESPONSE"
              text="Coordinate incidents, assign owners and accelerate resolution."
              href="/incidents"
            />
          </div>
        </div>
      </section>

      {/* =========================================================
          SECURITY PANEL
      ========================================================= */}

      <section
        id="security"
        className="relative z-10 border-t border-orange-500/10 bg-[#080807] px-5 py-24 sm:px-8"
      >
        <div className="mx-auto max-w-[1200px]">
          <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
            <div>
              <p className="font-mono text-[10px] tracking-[0.3em] text-emerald-500">
                SECURITY_INTELLIGENCE
              </p>

              <h2 className="mt-4 font-mono text-3xl uppercase sm:text-5xl">
                Continuous
                <br />
                <span className="text-orange-500">security visibility.</span>
              </h2>

              <p className="mt-6 max-w-xl font-mono text-xs leading-7 text-zinc-600">
                CONNECT RISKS, CONTROLS, EVIDENCE, AUDITS AND INCIDENTS TO
                UNDERSTAND YOUR SECURITY POSTURE AND RESPOND BEFORE THREATS
                BECOME BUSINESS IMPACT.
              </p>

              <Link
                href="/dashboard"
                className="group mt-8 inline-flex items-center gap-3 border border-orange-500/40 px-6 py-3 font-mono text-xs font-bold tracking-widest text-orange-400 transition hover:bg-orange-500 hover:text-black"
              >
                OPEN DASHBOARD
                <ArrowRight
                  size={15}
                  className="transition-transform group-hover:translate-x-1"
                />
              </Link>
            </div>

            {/* Security visualization */}
            <div className="relative h-[350px] overflow-hidden border border-orange-500/10 bg-black">
              <div className="cyber-grid absolute inset-0 opacity-30" />

              {/* Radar */}
              <div className="absolute left-1/2 top-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full border border-emerald-500/10">
                <div className="absolute inset-8 rounded-full border border-emerald-500/10" />
                <div className="absolute inset-16 rounded-full border border-emerald-500/10" />

                <div className="radar-sweep absolute left-1/2 top-1/2 h-1/2 w-px origin-bottom bg-gradient-to-t from-emerald-500/80 to-transparent" />
              </div>

              {/* Center */}
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
                <div className="flex h-14 w-14 items-center justify-center rounded-full border border-emerald-500/50 bg-emerald-500/5">
                  <Radar size={20} className="text-emerald-400" />
                </div>
              </div>

              {/* Floating labels */}
              <CyberLabel
                icon={<Cpu size={13} />}
                text="THREAT ENGINE"
                className="left-5 top-5"
              />

              <CyberLabel
                icon={<Network size={13} />}
                text="NETWORK SECURE"
                className="right-5 top-5"
              />

              <CyberLabel
                icon={<Terminal size={13} />}
                text="AUDIT READY"
                className="bottom-5 left-5"
              />

              <CyberLabel
                icon={<LockKeyhole size={13} />}
                text="ENCRYPTED"
                className="bottom-5 right-5"
              />
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================
          CTA
      ========================================================= */}

      <section className="relative z-10 px-5 py-24 sm:px-8">
        <div className="relative mx-auto max-w-[1100px] overflow-hidden border border-orange-500/20 bg-[#0a0907] px-6 py-16 text-center sm:px-12">
          <div className="cyber-grid absolute inset-0 opacity-20" />

          <div className="relative">
            <p className="font-mono text-[10px] tracking-[0.35em] text-orange-500">
              INITIALIZE_SECURITY
            </p>

            <h2 className="mt-5 font-mono text-3xl uppercase sm:text-5xl">
              Take control of your
              <span className="block text-orange-500">
                security ecosystem.
              </span>
            </h2>

            <p className="mx-auto mt-6 max-w-xl font-mono text-xs leading-7 text-zinc-600">
              ACCESS THE CYGRC CONSOLE AND BUILD A CONTINUOUS, INTELLIGENT
              GOVERNANCE AND SECURITY OPERATING MODEL.
            </p>

            <div className="mt-9 flex flex-wrap justify-center gap-3">
              <Link
                href="/login"
                className="bg-orange-500 px-7 py-3.5 font-mono text-xs font-bold tracking-widest text-black transition hover:bg-orange-400"
              >
                ACCESS CONSOLE
              </Link>

              <Link
                href="/signup"
                className="border border-zinc-700 px-7 py-3.5 font-mono text-xs font-bold tracking-widest text-zinc-300 transition hover:border-emerald-500 hover:text-emerald-400"
              >
                CREATE ACCOUNT
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================
          FOOTER
      ========================================================= */}

      <footer className="relative z-10 border-t border-orange-500/10 bg-black px-5 py-8 sm:px-8">
        <div className="mx-auto flex max-w-[1200px] flex-col items-center justify-between gap-4 md:flex-row">
          <div className="font-mono text-[9px] tracking-[0.2em] text-zinc-700">
            © {new Date().getFullYear()} CYGRC PLATFORM // ALL SYSTEMS
            RESERVED
          </div>

          <div className="flex gap-6 font-mono text-[9px] tracking-[0.15em] text-zinc-600">
            <Link href="/login" className="transition hover:text-orange-400">
              LOGIN
            </Link>

            <Link href="/signup" className="transition hover:text-orange-400">
              SIGNUP
            </Link>

            <Link
              href="/dashboard"
              className="transition hover:text-orange-400"
            >
              DASHBOARD
            </Link>
          </div>
        </div>
      </footer>

      {/* =========================================================
          GLOBAL CSS
      ========================================================= */}

      <style jsx global>{`
        @import url("https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap");

        .cyber-home {
          font-family: "Rajdhani", sans-serif;
        }

        .cyber-home .font-mono {
          font-family: "Share Tech Mono", monospace;
        }

        .cyber-grid {
          background-image:
            linear-gradient(rgba(249, 115, 22, 0.035) 1px, transparent 1px),
            linear-gradient(
              90deg,
              rgba(249, 115, 22, 0.035) 1px,
              transparent 1px
            );
          background-size: 50px 50px;
        }

        .cyber-gradient {
          background: linear-gradient(
            90deg,
            #ff7300 0%,
            #ff9d00 25%,
            #d4d947 50%,
            #54d77b 75%,
            #10b981 100%
          );
          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;
          background-size: 200% auto;
          animation: gradientMove 5s linear infinite;
        }

        .scan-line {
          animation: scanLine 7s linear infinite;
        }

        .network-line {
          position: absolute;
          left: 0;
          top: 50%;
          height: 1px;
          width: 50%;
          transform-origin: right center;
          background: linear-gradient(
            90deg,
            transparent,
            rgba(249, 115, 22, 0.05),
            rgba(249, 115, 22, 0.8)
          );
        }

        .network-line-1 {
          transform: rotate(18deg);
        }

        .network-line-2 {
          transform: rotate(9deg);
        }

        .network-line-3 {
          transform: rotate(-10deg);
        }

        .network-line-4 {
          transform: rotate(-18deg);
        }

        .network-line-5 {
          transform: rotate(3deg);
        }

        .radar-ring {
          animation: radarPulse 2s ease-out infinite;
        }

        .radar-sweep {
          animation: radarSweep 3s linear infinite;
        }

        .cyber-button {
          box-shadow:
            0 0 20px rgba(249, 115, 22, 0.15),
            inset 0 0 20px rgba(255, 255, 255, 0.03);
        }

        @keyframes gradientMove {
          0% {
            background-position: 0% center;
          }

          100% {
            background-position: 200% center;
          }
        }

        @keyframes scanLine {
          0% {
            transform: translateY(-100vh);
            opacity: 0;
          }

          10% {
            opacity: 1;
          }

          90% {
            opacity: 1;
          }

          100% {
            transform: translateY(100vh);
            opacity: 0;
          }
        }

        @keyframes radarPulse {
          0% {
            transform: scale(0.8);
            opacity: 0.8;
          }

          100% {
            transform: scale(1.6);
            opacity: 0;
          }
        }

        @keyframes radarSweep {
          from {
            transform: rotate(0deg);
          }

          to {
            transform: rotate(360deg);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .scan-line,
          .radar-ring,
          .radar-sweep,
          .cyber-gradient {
            animation: none;
          }
        }
      `}</style>
    </main>
  );
}

/* =========================================================
   NAV LINK
========================================================= */

function CyberNavLink({
  href,
  text,
}: {
  href: string;
  text: string;
}) {
  return (
    <Link
      href={href}
      className="group relative font-mono text-[10px] tracking-[0.18em] text-zinc-600 transition hover:text-orange-400"
    >
      {text}

      <span className="absolute -bottom-2 left-0 h-px w-0 bg-orange-500 transition-all duration-300 group-hover:w-full" />
    </Link>
  );
}

/* =========================================================
   PARTICLES
========================================================= */

function CyberParticles() {
  const particles = [
    [5, 16],
    [9, 62],
    [13, 42],
    [17, 79],
    [22, 27],
    [26, 66],
    [31, 18],
    [35, 83],
    [39, 36],
    [44, 70],
    [49, 13],
    [53, 88],
    [58, 31],
    [62, 73],
    [67, 20],
    [72, 57],
    [77, 84],
    [82, 29],
    [87, 68],
    [91, 42],
    [96, 17],
    [94, 78],
    [73, 10],
    [29, 50],
    [57, 52],
  ];

  return (
    <>
      {particles.map(([left, top], index) => (
        <span
          key={index}
          className={`absolute h-[2px] w-[2px] rounded-full ${
            index % 4 === 0 ? "bg-emerald-400" : "bg-orange-400"
          } particle`}
          style={{
            left: `${left}%`,
            top: `${top}%`,
            animationDelay: `${index * 0.17}s`,
          }}
        />
      ))}
    </>
  );
}

/* =========================================================
   DATA NODE
========================================================= */

function DataNode({
  className,
  green = false,
}: {
  className: string;
  green?: boolean;
}) {
  return (
    <div className={`absolute ${className}`}>
      <div
        className={`h-2.5 w-2.5 rounded-full ${
          green ? "bg-emerald-400" : "bg-orange-400"
        } shadow-[0_0_12px_currentColor] animate-pulse`}
      />
    </div>
  );
}

/* =========================================================
   SYSTEM CARD
========================================================= */

function SystemCard({
  icon,
  label,
  value,
  status,
  danger = false,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  status: string;
  danger?: boolean;
}) {
  return (
    <div className="group bg-[#070706] p-6 transition hover:bg-orange-500/[0.03]">
      <div className="flex items-center justify-between">
        <span className="text-orange-500/70">{icon}</span>

        <span className="font-mono text-[8px] tracking-widest text-zinc-700">
          DATA_STREAM
        </span>
      </div>

      <p className="mt-7 font-mono text-[9px] tracking-[0.2em] text-zinc-600">
        {label}
      </p>

      <p className="mt-2 font-mono text-4xl text-white">{value}</p>

      <p
        className={`mt-2 font-mono text-[9px] tracking-widest ${
          danger ? "text-red-500" : "text-emerald-500"
        }`}
      >
        {status}
      </p>

      <div className="mt-5 h-px w-full bg-zinc-900">
        <div
          className={`h-px ${
            danger ? "w-2/3 bg-red-500" : "w-4/5 bg-emerald-500"
          } transition-all duration-1000 group-hover:w-full`}
        />
      </div>
    </div>
  );
}

/* =========================================================
   FEATURE
========================================================= */

function CyberFeature({
  icon,
  number,
  title,
  text,
  href,
}: {
  icon: React.ReactNode;
  number: string;
  title: string;
  text: string;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="group relative overflow-hidden border border-zinc-900 bg-[#080807] p-6 transition duration-500 hover:border-orange-500/30"
    >
      <div className="absolute right-0 top-0 h-16 w-16 border-r border-t border-orange-500/0 transition group-hover:border-orange-500/30" />

      <div className="flex items-center justify-between">
        <div className="flex h-10 w-10 items-center justify-center border border-orange-500/20 text-orange-500 transition group-hover:border-orange-500/60 group-hover:bg-orange-500/10">
          {icon}
        </div>

        <span className="font-mono text-[10px] tracking-widest text-zinc-800">
          {number}
        </span>
      </div>

      <h3 className="mt-7 font-mono text-sm tracking-[0.15em] text-white">
        {title}
      </h3>

      <p className="mt-3 font-mono text-[10px] leading-6 text-zinc-600">
        {text}
      </p>

      <div className="mt-6 flex items-center gap-2 font-mono text-[9px] tracking-widest text-orange-500">
        ACCESS MODULE
        <ArrowRight
          size={12}
          className="transition-transform group-hover:translate-x-2"
        />
      </div>
    </Link>
  );
}

/* =========================================================
   SECURITY LABEL
========================================================= */

function CyberLabel({
  icon,
  text,
  className,
}: {
  icon: React.ReactNode;
  text: string;
  className: string;
}) {
  return (
    <div
      className={`absolute flex items-center gap-2 border border-zinc-900 bg-black/70 px-3 py-2 font-mono text-[8px] tracking-widest text-zinc-600 ${className}`}
    >
      <span className="text-emerald-500">{icon}</span>
      {text}
    </div>
  );
}