import dynamic from "next/dynamic";

const StockAnalysisForm = dynamic(() => import("@/components/StockAnalysisForm"), { ssr: false });

export default function AnalysisPage() {
  return <StockAnalysisForm />;
} 