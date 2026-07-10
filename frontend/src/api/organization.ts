import { apiRequest } from "@/api/client";
import type { OrganizationResponse } from "@/types/organization";

export function getOrganization(): Promise<OrganizationResponse> {
  return apiRequest<OrganizationResponse>("/organization");
}
