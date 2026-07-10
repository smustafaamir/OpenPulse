export const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "/api/v1";

export const WS_BASE =
  import.meta.env.VITE_WS_BASE_URL?.replace(/\/$/, "") || "";
