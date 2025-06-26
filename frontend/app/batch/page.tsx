import dynamic from "next/dynamic";
const BatchAnalysisForm = dynamic(() => import("@/components/BatchAnalysisForm"), { ssr: false });
export default function BatchPage() {
  return <BatchAnalysisForm />;
} 