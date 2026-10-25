import { AppShell } from "@/components/AppShell";
import { ScanDashboard } from "@/components/ScanDashboard";

export default function DashboardPage() {
  return (
    <AppShell active="dashboard">
      <ScanDashboard />
    </AppShell>
  );
}
