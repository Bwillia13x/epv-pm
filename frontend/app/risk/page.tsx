import dynamic from "next/dynamic";
const RiskMetricsForm = dynamic(() => import("@/components/RiskMetricsForm"), { ssr: false });
export default function RiskPage() {
  return <RiskMetricsForm />;
} 