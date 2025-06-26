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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  symbols: z
    .string()
    .min(1, { message: "Please enter at least one symbol." })
    .refine(
      (val) =>
        val
          .split(/[,\s]+/)
          .map((s) => s.trim())
          .filter(Boolean).length > 0,
      { message: "Please enter valid comma or space-separated tickers." }
    ),
});

export default function BatchAnalysisForm() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[] | null>(null);
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      symbols: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setLoading(true);
    setResults(null);

    const symbols = values.symbols
      .split(/[,\s]+/)
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);

    try {
      const data = await api.batchAnalysis(symbols);
      setResults(data.results || []);
      toast({
        title: "Batch Analysis Complete",
        description: `Successfully analyzed ${data.results.length} symbols.`,
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
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>Batch EPV Analysis</CardTitle>
        <CardDescription>
          Enter comma or space-separated stock tickers to perform a batch
          Earnings Power Value analysis.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="symbols"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Stock Symbols</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="e.g., AAPL, MSFT, GOOGL"
                      {...field}
                      disabled={loading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Symbols"}
            </Button>
          </form>
        </Form>

        {results && results.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>EPV/Share</TableHead>
                    <TableHead>MOS</TableHead>
                    <TableHead>Quality</TableHead>
                    <TableHead>Rec</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results.map((r) => (
                    <TableRow key={r.symbol}>
                      <TableCell className="font-medium">{r.symbol}</TableCell>
                      <TableCell>${r.current_price?.toFixed(2)}</TableCell>
                      <TableCell>${r.epv_per_share?.toFixed(2)}</TableCell>
                      <TableCell>
                        {((r.margin_of_safety || 0) * 100).toFixed(1)}%
                      </TableCell>
                      <TableCell>{r.quality_score?.toFixed(2)}</TableCell>
                      <TableCell>{r.recommendation}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
        )}

        {results && results.length === 0 && !loading && (
          <p className="mt-4 text-center text-gray-500">No results found for the given symbols.</p>
        )}
      </CardContent>
    </Card>
  );
}