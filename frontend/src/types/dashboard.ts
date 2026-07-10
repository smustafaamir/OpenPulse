export interface DashboardCreate {
  name: string;
  layout?: Record<string, unknown>;
}

export interface DashboardUpdate {
  name?: string;
  layout?: Record<string, unknown>;
}

export interface DashboardResponse {
  id: string;
  organization_id: string;
  name: string;
  layout: Record<string, unknown>;
}

export interface DashboardLayout {
  widgets: string[];
  selectedSymbol?: string;
  [key: string]: unknown;
}
