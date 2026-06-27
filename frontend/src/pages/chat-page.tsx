import { useMutation, useQuery } from "@tanstack/react-query";
import { Send } from "lucide-react";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { ErrorState } from "@/components/error-state";
import { LoadingSpinner } from "@/components/loading-spinner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { chatApi, getErrorMessage, reportsApi } from "@/lib/api";
import type { ChatMessage } from "@/types/api";

export function ChatPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [reportId, setReportId] = useState(searchParams.get("reportId") ?? "");
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<ChatMessage[]>([]);

  const reportsQuery = useQuery({
    queryKey: ["reports", "chat-options"],
    queryFn: () => reportsApi.list({ page: 1, page_size: 50 }),
  });

  const chatMutation = useMutation({
    mutationFn: chatApi.send,
    onSuccess: (response) => {
      setHistory(response.conversation_history);
      setMessage("");
    },
  });

  useEffect(() => {
    if (reportId) {
      setSearchParams({ reportId });
    }
  }, [reportId, setSearchParams]);

  if (reportsQuery.isLoading) return <LoadingSpinner label="Loading reports..." />;
  if (reportsQuery.isError) return <ErrorState message={getErrorMessage(reportsQuery.error)} />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">AI Kundali chat</h2>
        <p className="text-muted-foreground">Ask natural-language questions about a saved report using POST /api/v1/chat.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Select report context</CardTitle>
          <CardDescription>The chat engine uses consultation brain, fusion, dasha, and transit evidence from the saved report.</CardDescription>
        </CardHeader>
        <CardContent>
          <Select value={reportId || "none"} onValueChange={(value) => setReportId(value === "none" ? "" : value)}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a report" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Select report</SelectItem>
              {reportsQuery.data?.items.map((report) => (
                <SelectItem key={report.report_id} value={report.report_id}>
                  {report.lagna_sign ?? "Report"} / {report.moon_sign ?? "Moon"} — {report.report_id.slice(0, 8)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card className="flex min-h-[520px] flex-col">
        <CardHeader>
          <CardTitle>Conversation</CardTitle>
          {chatMutation.data && (
            <CardDescription>
              Model {chatMutation.data.model} · Source {chatMutation.data.source}
            </CardDescription>
          )}
        </CardHeader>
        <CardContent className="flex flex-1 flex-col gap-4">
          <ScrollArea className="h-[360px] rounded-md border p-4">
            <div className="space-y-4">
              {history.length === 0 && (
                <p className="text-sm text-muted-foreground">Ask about marriage, career, finance, health, or timing.</p>
              )}
              {history.map((entry, index) => (
                <div
                  key={`${entry.role}-${index}`}
                  className={`max-w-[85%] rounded-lg px-4 py-3 text-sm ${
                    entry.role === "user" ? "ml-auto bg-primary text-primary-foreground" : "bg-muted"
                  }`}
                >
                  {entry.content}
                </div>
              ))}
            </div>
          </ScrollArea>

          {chatMutation.isError && <p className="text-sm text-destructive">{getErrorMessage(chatMutation.error)}</p>}

          <form
            className="flex gap-2"
            onSubmit={(event) => {
              event.preventDefault();
              if (!reportId || !message.trim()) return;
              chatMutation.mutate({
                report_id: reportId,
                user_message: message.trim(),
                conversation_history: history,
              });
            }}
          >
            <Input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Why is marriage delayed according to my chart?"
              disabled={!reportId || chatMutation.isPending}
            />
            <Button type="submit" disabled={!reportId || !message.trim() || chatMutation.isPending}>
              <Send className="h-4 w-4" />
              Send
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
