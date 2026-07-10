import { useQuery } from "@tanstack/react-query";
import { getOrganization } from "@/api/organization";
import { Card } from "@/components/ui/Card";

export function SettingsPage() {
  const organizationQuery = useQuery({
    queryKey: ["organization"],
    queryFn: getOrganization,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-white">Settings</h2>
        <p className="text-sm text-slate-400">Organization details and integrations</p>
      </div>

      <Card title="Organization">
        {organizationQuery.isLoading ? (
          <p className="text-sm text-slate-500">Loading organization...</p>
        ) : organizationQuery.isError ? (
          <p className="text-sm text-rose-400">Failed to load organization.</p>
        ) : (
          <dl className="grid gap-3 text-sm">
            <div>
              <dt className="text-slate-500">Name</dt>
              <dd className="text-slate-100">{organizationQuery.data?.name}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Organization ID</dt>
              <dd className="font-mono text-slate-300">{organizationQuery.data?.id}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Created</dt>
              <dd className="text-slate-300">
                {organizationQuery.data?.created_at
                  ? new Date(organizationQuery.data.created_at).toLocaleString()
                  : "—"}
              </dd>
            </div>
          </dl>
        )}
      </Card>

      <Card title="API Keys">
        <p className="text-sm text-slate-400">
          API key management is planned for v0.2. You will be able to create and revoke
          keys for programmatic event ingestion here.
        </p>
      </Card>
    </div>
  );
}
