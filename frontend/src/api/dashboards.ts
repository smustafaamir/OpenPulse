import { apiRequest } from "@/api/client";
import type {
  DashboardCreate,
  DashboardResponse,
  DashboardUpdate,
} from "@/types/dashboard";

export function listDashboards(): Promise<DashboardResponse[]> {
  return apiRequest<DashboardResponse[]>("/dashboards");
}

export function getDashboard(dashboardId: string): Promise<DashboardResponse> {
  return apiRequest<DashboardResponse>(`/dashboards/${dashboardId}`);
}

export function createDashboard(data: DashboardCreate): Promise<DashboardResponse> {
  return apiRequest<DashboardResponse>("/dashboards", {
    method: "POST",
    body: data,
  });
}

export function updateDashboard(
  dashboardId: string,
  data: DashboardUpdate,
): Promise<DashboardResponse> {
  return apiRequest<DashboardResponse>(`/dashboards/${dashboardId}`, {
    method: "PATCH",
    body: data,
  });
}
