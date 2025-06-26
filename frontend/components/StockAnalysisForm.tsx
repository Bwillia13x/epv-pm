"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  symbol: z.string().min(1, { message: "Please enter a stock symbol." }),
});

export default function StockAnalysisForm() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      symbol: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setLoading(true);
    setResult(null);

    try {
      const data = await api.analyzeStock(values.symbol.trim().toUpperCase());
      setResult(data);
      toast({
        title: "Stock Analysis Complete",
        description: `Successfully analyzed ${data.symbol}.`,
      });
    } catch (err: any) {
      toast({
        title: "Analysis Failed",
        description: err.message || "There was an error performing the analysis.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="w-full max-w-xl mx-auto">
      <CardHeader>
        <CardTitle>Stock EPV Analysis</CardTitle>
        <CardDescription>
          Enter a stock ticker to perform an Earnings Power Value analysis.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="symbol"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Stock Symbol</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="e.g., AAPL"
                      {...field}
                      disabled={loading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Stock"}
            </Button>
          </form>
        </Form>

        {result && (
          <div className="mt-8 p-4 border rounded-md bg-gray-50 dark:bg-gray-800">
            <h2 className="text-lg font-semibold mb-2">{result.symbol} Analysis:</h2>
            <ul className="list-disc list-inside space-y-1">
              <li>
                <strong>Current Price:</strong> ${result.current_price?.toFixed(2)}
              </li>
              <li>
                <strong>EPV per Share:</strong> ${result.epv_per_share?.toFixed(2)}
              </li>
              <li>
                <strong>Margin of Safety:</strong>
                {((result.margin_of_safety || 0) * 100).toFixed(1)}%
              </li>
              <li>
                <strong>Quality Score:</strong> {result.quality_score?.toFixed(2)}
              </li>
              <li>
                <strong>Recommendation:</strong> {result.recommendation}
              </li>
              <li>
                <strong>Target Price:</strong> ${result.target_price?.toFixed(2)}
              </li>
              <li>
                <strong>Confidence Level:</strong>
                {((result.confidence_level || 0) * 100).toFixed(1)}%
              </li>
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}