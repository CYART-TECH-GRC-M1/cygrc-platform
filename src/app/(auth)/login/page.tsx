"use client";

import { Card, CardContent, Button, Link } from "@heroui/react";
import CustomInput from "../../../components/ui/Input";
import { Logo } from "@/components/Logo";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mail,
  Lock,
  ArrowRight,
  Fingerprint,
  ShieldCheck,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle2,
  Loader2,
  Terminal,
  Activity,
  Cpu,
  ScanLine,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

interface FormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

interface FormErrors {
  email?: string;
  password?: string;
  form?: string;
}

interface PasswordStrength {
  score: number;
  label: string;
  feedback: string[];
}

const getPasswordStrength = (
  password: string
): PasswordStrength => {
  if (!password) {
    return {
      score: 0,
      label: "None",
      feedback: [],
    };
  }

  let score = 0;
  const feedback: string[] = [];

  if (password.length >= 8) score++;
  if (password.length >= 12) score++;

  if (/[a-z]/.test(password)) {
    score++;
  } else {
    feedback.push("Add lowercase letters");
  }

  if (/[A-Z]/.test(password)) {
    score++;
  } else {
    feedback.push("Add uppercase letters");
  }

  if (/\d/.test(password)) {
    score++;
  } else {
    feedback.push("Add numbers");
  }

  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?]/.test(password)) {
    score++;
  } else {
    feedback.push("Add special characters");
  }

  if (password.length < 8) {
    feedback.unshift("Use at least 8 characters");
  }

  if (/(.)\1{2,}/.test(password)) {
    score = Math.max(0, score - 1);
    feedback.push("Avoid repeating characters");
  }

  if (/^(password|admin|qwerty|123456)/i.test(password)) {
    score = 0;
    feedback.unshift("Password is too common");
  }

  if (score <= 1) {
    return {
      score,
      label: "Weak",
      feedback: feedback.slice(0, 2),
    };
  }

  if (score <= 3) {
    return {
      score,
      label: "Fair",
      feedback: feedback.slice(0, 2),
    };
  }

  if (score <= 4) {
    return {
      score,
      label: "Strong",
      feedback: feedback.slice(0, 2),
    };
  }

  return {
    score: 5,
    label: "Very Strong",
    feedback: feedback.slice(0, 2),
  };
};

export default function LoginPage() {
  const [showPassword, setShowPassword] =
    useState(false);

  const [formData, setFormData] =
    useState<FormData>({
      email: "",
      password: "",
      rememberMe: false,
    });

  const [errors, setErrors] =
    useState<FormErrors>({});

  const [isLoading, setIsLoading] =
    useState(false);

  const [isSuccess, setIsSuccess] =
    useState(false);

  const passwordStrength = useMemo(
    () =>
      getPasswordStrength(
        formData.password
      ),
    [formData.password]
  );

  /* =========================
     REMEMBERED EMAIL
  ========================= */

  useEffect(() => {
    const rememberedEmail =
      localStorage.getItem(
        "remembered_email"
      );

    if (rememberedEmail) {
      setFormData((prev) => ({
        ...prev,
        email: rememberedEmail,
        rememberMe: true,
      }));
    }
  }, []);

  /* =========================
     UPDATE FIELD
  ========================= */

  const updateField = (
    field: keyof FormData,
    value: string | boolean
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    setErrors((prev) => ({
      ...prev,
      [field]: undefined,
      form: undefined,
    }));
  };

  /* =========================
     VALIDATION
  ========================= */

  const validateForm = () => {
    const newErrors: FormErrors = {};

    if (!formData.email.trim()) {
      newErrors.email =
        "Email address is required.";
    } else if (
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
        formData.email
      )
    ) {
      newErrors.email =
        "Enter a valid email address.";
    }

    if (!formData.password) {
      newErrors.password =
        "Password is required.";
    } else if (
      formData.password.length < 8
    ) {
      newErrors.password =
        "Password must contain at least 8 characters.";
    }

    setErrors(newErrors);

    return (
      Object.keys(newErrors).length === 0
    );
  };

  /* =========================
     REMEMBER ME
  ========================= */

  const handleRememberMe = (
    checked: boolean
  ) => {
    updateField(
      "rememberMe",
      checked
    );

    if (
      checked &&
      formData.email.trim()
    ) {
      localStorage.setItem(
        "remembered_email",
        formData.email.trim()
      );
    } else {
      localStorage.removeItem(
        "remembered_email"
      );
    }
  };

  /* =========================
     LOGIN
  ========================= */

  const handleSubmit = async (
    e: React.FormEvent<HTMLFormElement>
  ) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    if (formData.rememberMe) {
      localStorage.setItem(
        "remembered_email",
        formData.email.trim()
      );
    } else {
      localStorage.removeItem(
        "remembered_email"
      );
    }

    try {
      /*
       * Replace this demo section with
       * your real backend login API.
       */

      await new Promise((resolve) =>
        setTimeout(resolve, 900)
      );

      setIsSuccess(true);

      localStorage.setItem(
        "auth_token",
        "demo-auth-token"
      );

      setTimeout(() => {
        window.location.href =
          "/dashboard";
      }, 700);
    } catch (error) {
      console.error(
        "Login error:",
        error
      );

      setErrors({
        form:
          "Unable to sign in. Please check your connection and try again.",
      });

      setIsLoading(false);
    }
  };

  return (
    <main className="cyber-login relative min-h-screen overflow-hidden bg-[#050504] text-white">

      {/* =====================================================
          BACKGROUND
      ===================================================== */}

      <div className="pointer-events-none fixed inset-0 overflow-hidden">

        {/* Grid */}
        <div className="cyber-grid absolute inset-0 opacity-50" />

        {/* Orange glow */}
        <motion.div
          animate={{
            x: [0, 80, 0],
            y: [0, 40, 0],
            scale: [1, 1.15, 1],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute -left-48 top-20 h-[500px] w-[500px] rounded-full bg-orange-600/10 blur-[150px]"
        />

        {/* Green glow */}
        <motion.div
          animate={{
            x: [0, -70, 0],
            y: [0, 60, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute -right-48 bottom-10 h-[500px] w-[500px] rounded-full bg-emerald-500/5 blur-[150px]"
        />

        {/* Particles */}
        <CyberParticles />

        {/* Scan line */}
        <div className="login-scan-line absolute left-0 top-0 h-px w-full bg-gradient-to-r from-transparent via-orange-500/60 to-transparent" />
      </div>

      {/* =====================================================
          TOP NAVIGATION
      ===================================================== */}

      <header className="relative z-50 border-b border-orange-500/10 bg-[#050504]/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-[1400px] items-center justify-between px-5 sm:px-8">

          {/* Logo */}
          <Link
            href="/"
            className="group flex items-center gap-3"
          >
            <div className="relative flex h-9 w-9 items-center justify-center border border-orange-500/50 bg-orange-500/5">
              <div className="absolute inset-1 border border-emerald-400/30" />

              <ShieldCheck
                size={18}
                className="text-orange-400 transition group-hover:text-emerald-400"
              />
            </div>

            <div>
              <div className="font-mono text-lg tracking-[0.28em]">
                CYGRC
              </div>

              <div className="font-mono text-[8px] tracking-[0.22em] text-zinc-600">
                SECURITY ECOSYSTEM
              </div>
            </div>
          </Link>

          {/* Status */}
          <div className="hidden items-center gap-7 font-mono text-[9px] tracking-[0.18em] text-zinc-700 sm:flex">
            <span>
              NETWORK:{" "}
              <span className="text-emerald-500">
                SECURE
              </span>
            </span>

            <span>
              SIGNAL:{" "}
              <span className="text-orange-500">
                STRONG
              </span>
            </span>

            <span>
              PROTOCOL:{" "}
              <span className="text-emerald-500">
                GRC-01
              </span>
            </span>
          </div>

          {/* Home */}
          <Link
            href="/"
            className="font-mono text-[10px] tracking-[0.18em] text-zinc-500 transition hover:text-orange-400"
          >
            ← HOME
          </Link>
        </div>
      </header>

      {/* =====================================================
          MAIN
      ===================================================== */}

      <div className="relative z-10 flex min-h-[calc(100vh-64px)] items-center justify-center px-4 py-12 sm:px-6">

        <div className="grid w-full max-w-[1100px] items-center gap-12 lg:grid-cols-[0.9fr_1fr]">

          {/* =================================================
              LEFT CYBER PANEL
          ================================================= */}

          <motion.div
            initial={{
              opacity: 0,
              x: -30,
            }}
            animate={{
              opacity: 1,
              x: 0,
            }}
            transition={{
              duration: 0.7,
            }}
            className="hidden lg:block"
          >

            <div className="relative">

              {/* Status */}
              <div className="mb-7 flex items-center gap-3 font-mono text-[10px] tracking-[0.3em] text-orange-500">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-orange-500 shadow-[0_0_12px_#f97316]" />
                AUTHENTICATION_PROTOCOL
              </div>

              {/* Heading */}
              <h1 className="font-mono text-5xl font-extralight uppercase leading-[0.95] tracking-[-0.04em] xl:text-6xl">
                SECURE
                <br />

                <span className="cyber-gradient">
                  ACCESS
                </span>

                <br />

                <span className="text-zinc-500">
                  ECOSYSTEM.
                </span>
              </h1>

              <p className="mt-7 max-w-md font-mono text-xs leading-7 tracking-[0.1em] text-zinc-600">
                AUTHORIZED PERSONNEL ONLY.
                <br />
                ACCESS THE CYGRC SECURITY
                OPERATIONS ENVIRONMENT.
              </p>

              {/* Security visualization */}
              <div className="relative mt-12 h-44 overflow-hidden border border-orange-500/10 bg-black/40">

                <div className="cyber-grid absolute inset-0 opacity-30" />

                {/* Horizontal line */}
                <div className="absolute left-0 right-0 top-1/2 h-px bg-orange-500/20" />

                {/* Vertical line */}
                <div className="absolute bottom-0 left-1/2 top-0 w-px bg-orange-500/10" />

                {/* Center */}
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">

                  <div className="absolute -inset-8 animate-pulse rounded-full bg-orange-500/10 blur-xl" />

                  <div className="relative flex h-12 w-12 items-center justify-center rounded-full border border-orange-500/60 bg-black shadow-[0_0_25px_rgba(249,115,22,0.4)]">
                    <ScanLine
                      size={18}
                      className="text-orange-400"
                    />
                  </div>

                  <div className="login-radar-ring absolute -inset-5 rounded-full border border-orange-500/20" />
                </div>

                {/* Lines */}
                <div className="absolute left-0 top-[35%] h-px w-[45%] bg-gradient-to-r from-transparent to-orange-500/50" />

                <div className="absolute bottom-[32%] right-0 h-px w-[40%] bg-gradient-to-l from-transparent to-emerald-500/40" />

                {/* Labels */}
                <div className="absolute left-3 top-3 font-mono text-[8px] tracking-widest text-zinc-700">
                  IDENTITY_SCAN
                </div>

                <div className="absolute right-3 top-3 font-mono text-[8px] tracking-widest text-zinc-700">
                  ACTIVE
                </div>

                <div className="absolute bottom-3 left-3 flex items-center gap-2 font-mono text-[8px] tracking-widest text-zinc-700">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  ENCRYPTED
                </div>

                <div className="absolute bottom-3 right-3 font-mono text-[8px] tracking-widest text-orange-500/70">
                  AUTH_READY
                </div>
              </div>

              {/* Bottom system info */}
              <div className="mt-7 grid grid-cols-3 gap-3">

                <MiniStatus
                  icon={<ShieldCheck size={13} />}
                  label="SECURE"
                />

                <MiniStatus
                  icon={<Activity size={13} />}
                  label="MONITOR"
                />

                <MiniStatus
                  icon={<Cpu size={13} />}
                  label="ACTIVE"
                />

              </div>
            </div>
          </motion.div>

          {/* =================================================
              LOGIN
          ================================================= */}

          <motion.div
            initial={{
              opacity: 0,
              y: 30,
              scale: 0.97,
            }}
            animate={{
              opacity: 1,
              y: 0,
              scale: 1,
            }}
            transition={{
              duration: 0.7,
              ease: "easeOut",
            }}
            className="w-full max-w-md justify-self-center lg:max-w-[480px]"
          >

            {/* Mobile Logo */}
            <div className="mb-7 flex flex-col items-center lg:hidden">

              <motion.div
                animate={{
                  y: [0, -5, 0],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
                className="relative"
              >
                <div className="absolute inset-0 rounded-full bg-orange-500/20 blur-2xl" />

                <Logo
                  size={62}
                  className="relative"
                />
              </motion.div>

              <h1 className="mt-4 font-mono text-2xl tracking-[0.2em]">
                CYGRC
              </h1>

              <p className="mt-1 font-mono text-[9px] tracking-widest text-zinc-600">
                SECURITY ECOSYSTEM
              </p>
            </div>

            {/* Card */}
            <Card
              className="
                overflow-hidden
                rounded-none
                border
                border-orange-500/20
                bg-[#090908]/95
                shadow-[0_30px_100px_rgba(0,0,0,0.7)]
                backdrop-blur-2xl
              "
            >

              {/* Top orange line */}
              <div className="h-px w-full bg-gradient-to-r from-transparent via-orange-500 to-transparent" />

              <CardContent className="p-6 sm:p-9">

                {/* Header */}
                <div className="mb-7">

                  <div className="mb-4 flex items-center justify-between">

                    <div className="flex items-center gap-2 font-mono text-[9px] tracking-[0.25em] text-orange-500">
                      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-orange-500 shadow-[0_0_10px_#f97316]" />
                      SECURE ACCESS
                    </div>

                    <span className="font-mono text-[8px] tracking-widest text-zinc-700">
                      AUTH_01
                    </span>

                  </div>

                  <h2 className="font-mono text-2xl tracking-wide text-white sm:text-3xl">
                    INITIALIZE SESSION
                  </h2>

                  <p className="mt-3 font-mono text-[10px] leading-6 tracking-wide text-zinc-600">
                    ENTER AUTHORIZED CREDENTIALS
                    TO ACCESS THE CYGRC SECURITY
                    CONSOLE.
                  </p>

                </div>

                {/* Error */}
                <AnimatePresence>
                  {errors.form && (
                    <motion.div
                      initial={{
                        opacity: 0,
                        height: 0,
                      }}
                      animate={{
                        opacity: 1,
                        height: "auto",
                      }}
                      exit={{
                        opacity: 0,
                        height: 0,
                      }}
                      className="mb-5 flex items-start gap-3 border border-red-500/20 bg-red-500/5 p-3 font-mono text-[10px] text-red-400"
                    >
                      <AlertCircle
                        size={16}
                        className="mt-0.5 shrink-0"
                      />

                      <span>
                        {errors.form}
                      </span>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Success */}
                <AnimatePresence>
                  {isSuccess && (
                    <motion.div
                      initial={{
                        opacity: 0,
                        scale: 0.96,
                      }}
                      animate={{
                        opacity: 1,
                        scale: 1,
                      }}
                      className="mb-5 flex items-center gap-3 border border-emerald-500/20 bg-emerald-500/5 p-3 font-mono text-[10px] text-emerald-400"
                    >
                      <CheckCircle2 size={16} />

                      <span>
                        AUTHENTICATION SUCCESSFUL.
                        REDIRECTING...
                      </span>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* FORM */}
                <form
                  onSubmit={handleSubmit}
                  className="space-y-6"
                >

                  {/* EMAIL */}
                  <div className="relative">

                    <CustomInput
                      label="IDENTITY / EMAIL"
                      type="email"
                      value={formData.email}
                      onChange={(e) =>
                        updateField(
                          "email",
                          e.target.value
                        )
                      }
                      placeholder="operator@company.com"
                      autoComplete="email"
                      error={errors.email}
                      className="
                        h-12
                        rounded-none
                        border-zinc-800
                        bg-black/60
                        pl-10
                        font-mono
                        text-sm
                        text-white
                        placeholder:text-zinc-700
                        focus:border-orange-500
                        dark:border-zinc-800
                        dark:bg-black/60
                        dark:text-white
                      "
                    />

                    <Mail
                      size={16}
                      className="pointer-events-none absolute left-3 top-[58px] z-10 -translate-y-1/2 text-zinc-600"
                    />

                  </div>

                  {/* PASSWORD */}
                  <div className="relative">

                    <CustomInput
                      label="ACCESS KEY / PASSWORD"
                      type={
                        showPassword
                          ? "text"
                          : "password"
                      }
                      value={formData.password}
                      onChange={(e) =>
                        updateField(
                          "password",
                          e.target.value
                        )
                      }
                      placeholder="Enter access key"
                      autoComplete="current-password"
                      error={errors.password}
                      className="
                        h-12
                        rounded-none
                        border-zinc-800
                        bg-black/60
                        pl-10
                        pr-12
                        font-mono
                        text-sm
                        text-white
                        placeholder:text-zinc-700
                        dark:border-zinc-800
                        dark:bg-black/60
                        dark:text-white
                      "
                    />

                    <Lock
                      size={16}
                      className="pointer-events-none absolute left-3 top-[58px] z-10 -translate-y-1/2 text-zinc-600"
                    />

                    <button
                      type="button"
                      aria-label={
                        showPassword
                          ? "Hide password"
                          : "Show password"
                      }
                      onClick={() =>
                        setShowPassword(
                          !showPassword
                        )
                      }
                      className="absolute right-3 top-[58px] z-10 -translate-y-1/2 p-1 text-zinc-600 transition hover:text-orange-400"
                    >
                      {showPassword ? (
                        <EyeOff size={17} />
                      ) : (
                        <Eye size={17} />
                      )}
                    </button>

                    {/* Strength */}
                    <AnimatePresence>
                      {formData.password &&
                        !errors.password && (
                          <motion.div
                            initial={{
                              opacity: 0,
                              y: -5,
                            }}
                            animate={{
                              opacity: 1,
                              y: 0,
                            }}
                            exit={{
                              opacity: 0,
                              y: -5,
                            }}
                            className="mt-3"
                          >

                            <div className="flex items-center gap-3">

                              <div className="h-1 flex-1 overflow-hidden bg-zinc-900">
                                <motion.div
                                  initial={{
                                    width: 0,
                                  }}
                                  animate={{
                                    width: `${
                                      (passwordStrength.score /
                                        5) *
                                      100
                                    }%`,
                                  }}
                                  className={`h-full ${
                                    passwordStrength.score <=
                                    1
                                      ? "bg-red-500"
                                      : passwordStrength.score <=
                                        3
                                      ? "bg-orange-500"
                                      : "bg-emerald-500"
                                  }`}
                                />
                              </div>

                              <span
                                className={`font-mono text-[8px] tracking-widest ${
                                  passwordStrength.score <=
                                  1
                                    ? "text-red-500"
                                    : passwordStrength.score <=
                                      3
                                    ? "text-orange-500"
                                    : "text-emerald-500"
                                }`}
                              >
                                {
                                  passwordStrength.label
                                }
                              </span>

                            </div>

                            {passwordStrength.feedback
                              .length > 0 && (
                              <div className="mt-2 font-mono text-[8px] tracking-wide text-zinc-700">
                                {passwordStrength.feedback.map(
                                  (
                                    item,
                                    index
                                  ) => (
                                    <div
                                      key={
                                        index
                                      }
                                      className="mt-1"
                                    >
                                      // {item}
                                    </div>
                                  )
                                )}
                              </div>
                            )}

                          </motion.div>
                        )}
                    </AnimatePresence>
                  </div>

                  {/* OPTIONS */}
                  <div className="flex items-center justify-between">

                    <label className="flex cursor-pointer items-center gap-2 font-mono text-[9px] tracking-wider text-zinc-600">
                      <input
                        type="checkbox"
                        checked={
                          formData.rememberMe
                        }
                        onChange={(e) =>
                          handleRememberMe(
                            e.target.checked
                          )
                        }
                        className="h-3.5 w-3.5 accent-orange-500"
                      />

                      REMEMBER SESSION
                    </label>

                    <Link
                      href="#"
                      className="font-mono text-[9px] tracking-wider text-zinc-600 transition hover:text-orange-400"
                    >
                      RECOVER ACCESS
                    </Link>

                  </div>

                  {/* SUBMIT */}
                  <motion.div
                    whileHover={{
                      scale: isLoading
                        ? 1
                        : 1.01,
                    }}
                    whileTap={{
                      scale: isLoading
                        ? 1
                        : 0.98,
                    }}
                  >
                    <Button
                      type="submit"
                      size="lg"
                      className="
                        h-12
                        w-full
                        rounded-none
                        bg-orange-500
                        font-mono
                        text-xs
                        font-bold
                        tracking-[0.18em]
                        text-black
                        shadow-[0_0_25px_rgba(249,115,22,0.12)]
                        transition
                        hover:bg-orange-400
                        hover:shadow-[0_0_35px_rgba(249,115,22,0.22)]
                      "
                    >
                      {isLoading ? (
                        <>
                          <Loader2
                            size={16}
                            className="mr-2 animate-spin"
                          />
                          AUTHENTICATING...
                        </>
                      ) : isSuccess ? (
                        <>
                          <CheckCircle2
                            size={16}
                            className="mr-2"
                          />
                          ACCESS GRANTED
                        </>
                      ) : (
                        <>
                          INITIALIZE SESSION
                          <ArrowRight
                            size={18}
                            className="ml-2"
                          />
                        </>
                      )}
                    </Button>
                  </motion.div>
                </form>

                {/* Divider */}
                <div className="my-7 flex items-center gap-3">
                  <div className="h-px flex-1 bg-zinc-900" />

                  <span className="font-mono text-[8px] tracking-[0.2em] text-zinc-700">
                    ALTERNATE_AUTH
                  </span>

                  <div className="h-px flex-1 bg-zinc-900" />
                </div>

                {/* SSO */}
                <motion.button
                  whileHover={{
                    y: -2,
                  }}
                  whileTap={{
                    scale: 0.98,
                  }}
                  type="button"
                  className="
                    group
                    flex
                    w-full
                    items-center
                    justify-center
                    gap-3
                    rounded-none
                    border
                    border-zinc-800
                    bg-black/40
                    px-5
                    py-3
                    font-mono
                    text-[9px]
                    tracking-[0.15em]
                    text-zinc-500
                    transition
                    hover:border-emerald-500/40
                    hover:text-emerald-400
                  "
                >
                  <Fingerprint
                    size={18}
                    className="text-emerald-500/70 transition group-hover:text-emerald-400"
                  />

                  CONTINUE WITH SSO /
                  BIOMETRICS
                </motion.button>

                {/* Security status */}
                <div className="mt-6 flex items-center justify-center gap-2 border-t border-zinc-900 pt-5 font-mono text-[8px] tracking-[0.15em] text-zinc-700">
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />

                  CONNECTION ENCRYPTED

                  <span className="text-zinc-900">
                    //
                  </span>

                  TLS SECURE
                </div>

              </CardContent>
            </Card>

            {/* Bottom register */}
            <motion.p
              initial={{
                opacity: 0,
              }}
              animate={{
                opacity: 1,
              }}
              transition={{
                delay: 0.8,
              }}
              className="mt-6 text-center font-mono text-[9px] tracking-widest text-zinc-700"
            >
              NO ACCESS CREDENTIALS?{" "}
              <Link
                href="/signup"
                className="text-orange-500 transition hover:text-orange-400"
              >
                REQUEST ACCESS
              </Link>
            </motion.p>

          </motion.div>
        </div>
      </div>

      {/* =====================================================
          FOOTER STATUS
      ===================================================== */}

      <div className="pointer-events-none absolute bottom-4 left-0 right-0 z-20 hidden px-5 md:block">
        <div className="mx-auto flex max-w-[1400px] justify-between font-mono text-[8px] tracking-[0.2em] text-zinc-800">
          <span>
            CYGRC_AUTH_NODE // 01
          </span>

          <span>
            SYS_STABILITY:{" "}
            <span className="text-emerald-500">
              100%
            </span>
          </span>

          <span>
            SESSION_PROTOCOL: ACTIVE
          </span>
        </div>
      </div>

      {/* =====================================================
          CSS
      ===================================================== */}

      <style jsx global>{`

        @import url("https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap");

        .cyber-login {
          font-family: "Rajdhani", sans-serif;
        }

        .cyber-login .font-mono {
          font-family: "Share Tech Mono", monospace;
        }

        .cyber-grid {
          background-image:
            linear-gradient(
              rgba(249, 115, 22, 0.035) 1px,
              transparent 1px
            ),
            linear-gradient(
              90deg,
              rgba(249, 115, 22, 0.035) 1px,
              transparent 1px
            );

          background-size: 45px 45px;
        }

        .cyber-gradient {
          background: linear-gradient(
            90deg,
            #ff7300 0%,
            #ff9d00 30%,
            #d4d947 55%,
            #54d77b 80%,
            #10b981 100%
          );

          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;

          background-size: 200% auto;

          animation: loginGradient 5s linear infinite;
        }

        .login-scan-line {
          animation: loginScan 8s linear infinite;
        }

        .login-radar-ring {
          animation: loginRadar 2s ease-out infinite;
        }

        @keyframes loginGradient {
          0% {
            background-position: 0% center;
          }

          100% {
            background-position: 200% center;
          }
        }

        @keyframes loginScan {
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

        @keyframes loginRadar {
          0% {
            transform: scale(0.8);
            opacity: 0.8;
          }

          100% {
            transform: scale(1.7);
            opacity: 0;
          }
        }

        @keyframes cyberParticle {
          0%,
          100% {
            opacity: 0.15;
            transform: translateY(0);
          }

          50% {
            opacity: 0.8;
            transform: translateY(-12px);
          }
        }

        .cyber-particle {
          animation: cyberParticle 3s ease-in-out infinite;
        }

        @media (prefers-reduced-motion: reduce) {
          .login-scan-line,
          .login-radar-ring,
          .cyber-gradient,
          .cyber-particle {
            animation: none;
          }
        }
      `}</style>
    </main>
  );
}

/* =========================================================
   PARTICLES
========================================================= */

function CyberParticles() {
  const particles = [
    [5, 15],
    [9, 32],
    [13, 72],
    [18, 45],
    [23, 20],
    [28, 83],
    [34, 30],
    [39, 65],
    [44, 14],
    [49, 77],
    [54, 28],
    [59, 88],
    [64, 40],
    [69, 18],
    [74, 70],
    [79, 32],
    [84, 82],
    [89, 50],
    [94, 22],
    [97, 68],
    [15, 90],
    [32, 52],
    [67, 92],
    [87, 12],
  ];

  return (
    <>
      {particles.map(
        ([left, top], index) => (
          <span
            key={index}
            className={`cyber-particle absolute h-[2px] w-[2px] rounded-full ${
              index % 4 === 0
                ? "bg-emerald-400"
                : "bg-orange-400"
            }`}
            style={{
              left: `${left}%`,
              top: `${top}%`,
              animationDelay: `${index * 0.18}s`,
            }}
          />
        )
      )}
    </>
  );
}

/* =========================================================
   MINI STATUS
========================================================= */

function MiniStatus({
  icon,
  label,
}: {
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <div className="border border-zinc-900 bg-black/30 p-3">
      <div className="text-emerald-500/70">
        {icon}
      </div>

      <p className="mt-2 font-mono text-[8px] tracking-widest text-zinc-700">
        {label}
      </p>
    </div>
  );
}