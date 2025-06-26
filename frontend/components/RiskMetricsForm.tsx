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
  prices: z
    .string()
    .min(1, { message: "Please enter at least two prices." })
    .refine(
      (val) => {
        const parsedPrices = val
          .split(/[\s,]+/)
          .map((p) => parseFloat(p))
          .filter((n) => !isNaN(n));
        return parsedPrices.length >= 2;
      },
      { message: "Please enter at least two valid numbers separated by spaces or commas." }
    ),
});

export default function RiskMetricsForm() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      prices: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setLoading(true);
    setResult(null);

    const prices = values.prices
      .split(/[\s,]+/)
      .map((p) => parseFloat(p))
      .filter((n) => !isNaN(n));

    try {
      const data = await api.riskMetrics(prices);
      setResult(data);
      toast({
        title: "Risk Metrics Calculated",
        description: "Successfully calculated risk metrics.",
      });
    } catch (err: any) {
      toast({
        title: "Calculation Failed",
        description: err.message || "There was an error calculating risk metrics.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="w-full max-w-xl mx-auto">
      <CardHeader>
        <CardTitle>Risk Metrics Calculator</CardTitle>
        <CardDescription>
          Enter a series of prices to calculate various risk metrics.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="prices"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Price Series</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="e.g., 100 101 99 102 105"
                      {...field}
                      disabled={loading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Calculating..." : "Calculate Risk Metrics"}
            </Button>
          </form>
        </Form>

        {result && (
          <div className="mt-8 p-4 border rounded-md bg-gray-50 dark:bg-gray-800">
            <h2 className="text-lg font-semibold mb-2">Results:</h2>
            <ul className="list-disc list-inside space-y-1">
              {Object.entries(result).map(([key, value]) => (
                <li key={key}>
                  <strong>{key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}</strong>: {typeof value === "number" ? value.toFixed(4) : String(value)}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}