import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ChevronDown, ChevronRight, Copy } from "lucide-react"
import { useApp } from "@/context/AppContext"

export function APILogsTab() {
  const { questions } = useApp()
  const [expandedLog, setExpandedLog] = useState<number | null>(null)

  const processedQuestions = questions.filter((q) => q.ai_processed).length
  const apiCalls = Math.ceil(processedQuestions / 10)

  const logs = Array.from({ length: apiCalls }, (_, i) => ({
    id: i + 1,
    timestamp: new Date(Date.now() - (apiCalls - i) * 30000).toISOString(),
    model: "google/gemini-flash-lite",
    batchId: `batch_${i + 1}`,
    status: "success",
    tokens: { input: 30000, output: 5000 },
    cost: 0.01228,
    time: 23400,
  }))

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Call Logs</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[50px]"></TableHead>
              <TableHead>Timestamp</TableHead>
              <TableHead>Model</TableHead>
              <TableHead>Batch ID</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Tokens</TableHead>
              <TableHead>Cost</TableHead>
              <TableHead>Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {logs.map((log) => (
              <>
                <TableRow key={log.id} className="cursor-pointer hover:bg-muted/50">
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        setExpandedLog(expandedLog === log.id ? null : log.id)
                      }
                    >
                      {expandedLog === log.id ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                    </Button>
                  </TableCell>
                  <TableCell className="text-xs">
                    {new Date(log.timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell className="text-xs font-mono">
                    {log.model.split("/")[1]}
                  </TableCell>
                  <TableCell className="text-xs font-mono">{log.batchId}</TableCell>
                  <TableCell>
                    <Badge className="bg-green-600">Success</Badge>
                  </TableCell>
                  <TableCell className="text-xs">
                    {(log.tokens.input + log.tokens.output).toLocaleString()}
                  </TableCell>
                  <TableCell className="text-xs">${log.cost.toFixed(4)}</TableCell>
                  <TableCell className="text-xs">{(log.time / 1000).toFixed(1)}s</TableCell>
                </TableRow>
                {expandedLog === log.id && (
                  <TableRow>
                    <TableCell colSpan={8}>
                      <div className="p-4 space-y-4">
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-sm">Request JSON</h4>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() =>
                                handleCopy(
                                  JSON.stringify(
                                    {
                                      model: log.model,
                                      messages: [
                                        {
                                          role: "system",
                                          content: "Review question quality...",
                                        },
                                      ],
                                      max_tokens: 7000,
                                      temperature: 0.2,
                                    },
                                    null,
                                    2
                                  )
                                )
                              }
                            >
                              <Copy className="h-4 w-4 mr-2" />
                              Copy
                            </Button>
                          </div>
                          <pre className="bg-gray-900 text-gray-100 p-4 rounded text-xs overflow-x-auto">
{JSON.stringify(
  {
    model: log.model,
    messages: [
      {
        role: "system",
        content: "Review the following questions for grammar, spelling, and punctuation errors...",
      },
      {
        role: "user",
        content: "Questions batch " + log.batchId,
      },
    ],
    max_tokens: 7000,
    temperature: 0.2,
    top_p: 1,
  },
  null,
  2
)}
                          </pre>
                        </div>
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-sm">Response JSON</h4>
                            <Button variant="ghost" size="sm">
                              <Copy className="h-4 w-4 mr-2" />
                              Copy
                            </Button>
                          </div>
                          <pre className="bg-gray-900 text-gray-100 p-4 rounded text-xs overflow-x-auto">
{JSON.stringify(
  {
    id: `call_${log.id}`,
    model: log.model,
    usage: log.tokens,
    choices: [
      {
        message: {
          role: "assistant",
          content: "Assessment completed for 10 questions...",
        },
      },
    ],
  },
  null,
  2
)}
                          </pre>
                        </div>
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
