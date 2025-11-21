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

  // Create more log entries (multiply to get 2-3x more)
  const baseApiCalls = Math.ceil(processedQuestions / 10)
  const totalLogs = Math.max(baseApiCalls * 3, 5) // At least 5 logs for demo

  const logs = Array.from({ length: totalLogs }, (_, i) => ({
    id: i + 1,
    timestamp: new Date(Date.now() - (totalLogs - i) * 30000).toISOString(),
    model: "google/gemini-2.5-flash-lite-preview-09-2025",
    batchId: `batch_${String(i + 1).padStart(3, '0')}`,
    status: "success",
    tokens: {
      input: 28000 + Math.floor(Math.random() * 4000),
      output: 4500 + Math.floor(Math.random() * 1500)
    },
    cost: 0.01228 + Math.random() * 0.005,
    time: 22000 + Math.floor(Math.random() * 3000),
    questionIds: Array.from({ length: 10 }, (_, j) => 150000 + (i * 10) + j),
  }))

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const getDetailedResponse = (log: typeof logs[0]) => ({
    id: `gen-${Date.now()}-${Math.random().toString(36).substr(2, 20)}`,
    provider: "Google AI Studio",
    model: log.model,
    object: "chat.completion",
    created: Math.floor(new Date(log.timestamp).getTime() / 1000),
    choices: [
      {
        logprobs: null,
        finish_reason: "stop",
        native_finish_reason: "STOP",
        index: 0,
        message: {
          role: "assistant",
          content: JSON.stringify([
            {
              questionid: log.questionIds[0],
              change_required: 1,
              feedback: {
                question: {
                  issue: "Missing question mark at end.",
                  rewrite: "<p>Which of the following is correct?</p>"
                },
                answer1: { issue: "No changes needed.", rewrite: "" },
                answer2: { issue: "Spelling error: 'hurrily' should be 'hurriedly'.", rewrite: "<p>always eating food hurriedly</p>" },
                answer3: { issue: "No changes needed.", rewrite: "" },
                answer4: { issue: "No changes needed.", rewrite: "" }
              }
            },
            {
              questionid: log.questionIds[1],
              change_required: 0,
              feedback: {
                question: { issue: "No changes needed.", rewrite: "" },
                answer1: { issue: "No changes needed.", rewrite: "" },
                answer2: { issue: "No changes needed.", rewrite: "" },
                answer3: { issue: "No changes needed.", rewrite: "" },
                answer4: { issue: "No changes needed.", rewrite: "" }
              }
            }
          ], null, 2)
        }
      }
    ],
    usage: {
      prompt_tokens: log.tokens.input,
      completion_tokens: log.tokens.output,
      total_tokens: log.tokens.input + log.tokens.output
    }
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Call Logs ({logs.length} calls)</CardTitle>
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
                    {log.model.split("/")[1].substring(0, 20)}...
                  </TableCell>
                  <TableCell className="text-xs font-mono">{log.batchId}</TableCell>
                  <TableCell>
                    <Badge className="bg-green-600">Success</Badge>
                  </TableCell>
                  <TableCell className="text-xs">
                    {(log.tokens.input + log.tokens.output).toLocaleString()}
                  </TableCell>
                  <TableCell className="text-xs">${log.cost.toFixed(5)}</TableCell>
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
                                          content: "You are an expert educational content quality reviewer...",
                                        },
                                        {
                                          role: "user",
                                          content: `Process batch ${log.batchId} with ${log.questionIds.length} questions`,
                                        },
                                      ],
                                      max_tokens: 7000,
                                      temperature: 0.2,
                                      top_p: 1,
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
                          <pre className="bg-gray-900 text-gray-100 p-4 rounded text-xs overflow-x-auto max-h-[300px] overflow-y-auto">
{JSON.stringify(
  {
    model: log.model,
    messages: [
      {
        role: "system",
        content: "You are an expert educational content quality reviewer, combining the precision of a proof-reader and the discernment of a subject matter expert (SME). Your role is to assess MCQ-type questions for grammar, spelling, punctuation, clarity, and adherence to professional educational style standards...",
      },
      {
        role: "user",
        content: JSON.stringify(
          log.questionIds.map(qid => ({
            questionid: qid,
            question: "<p>Sample question text...</p>",
            answer1: "<p>Option A</p>",
            answer2: "<p>Option B</p>",
            answer3: "<p>Option C</p>",
            answer4: "<p>Option D</p>",
          }))
        ),
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
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleCopy(JSON.stringify(getDetailedResponse(log), null, 2))}
                            >
                              <Copy className="h-4 w-4 mr-2" />
                              Copy
                            </Button>
                          </div>
                          <pre className="bg-gray-900 text-gray-100 p-4 rounded text-xs overflow-x-auto max-h-[400px] overflow-y-auto">
{JSON.stringify(getDetailedResponse(log), null, 2)}
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
