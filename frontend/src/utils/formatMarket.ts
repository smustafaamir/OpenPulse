export type PercentTone = "positive" | "negative" | "neutral";

export interface FormattedPercent {
  text: string;
  tone: PercentTone;
}

function priceFractionDigits(value: number): { min: number; max: number } {
  const abs = Math.abs(value);
  if (abs >= 10_000) {
    return { min: 2, max: 2 };
  }
  if (abs >= 100) {
    return { min: 2, max: 2 };
  }
  if (abs >= 1) {
    return { min: 2, max: 4 };
  }
  return { min: 4, max: 6 };
}

export function formatPrice(value: unknown, currency = "USD"): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "—";
  }
  const { min, max } = priceFractionDigits(value);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: min,
    maximumFractionDigits: max,
  }).format(value);
}

export function formatPriceCompact(value: unknown, currency = "USD"): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "—";
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatPercent(value: unknown): FormattedPercent {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return { text: "—", tone: "neutral" };
  }
  const sign = value > 0 ? "+" : "";
  const tone: PercentTone = value > 0 ? "positive" : value < 0 ? "negative" : "neutral";
  return {
    text: `${sign}${value.toFixed(2)}%`,
    tone,
  };
}

export function formatVolume(value: unknown): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "—";
  }
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatMarketTime(iso: string): string {
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(new Date(iso));
}

export function formatTradingPair(
  symbol: string,
  payload: Record<string, unknown>,
): string {
  if (typeof payload.pair === "string") {
    const pair = payload.pair.toUpperCase();
    if (pair.endsWith("USDT")) {
      return `${pair.slice(0, -4)}/USDT`;
    }
    return pair;
  }
  return `${symbol}/USDT`;
}

export function percentToneClass(tone: PercentTone): string {
  if (tone === "positive") {
    return "text-emerald-300";
  }
  if (tone === "negative") {
    return "text-rose-300";
  }
  return "text-slate-400";
}

export function percentBadgeClass(tone: PercentTone): string {
  if (tone === "positive") {
    return "bg-emerald-500/15 text-emerald-300 ring-emerald-500/25";
  }
  if (tone === "negative") {
    return "bg-rose-500/15 text-rose-300 ring-rose-500/25";
  }
  return "bg-slate-500/15 text-slate-400 ring-slate-500/25";
}
