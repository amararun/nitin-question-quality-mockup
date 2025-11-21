import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { useApp } from "@/context/AppContext"
import { Loader2, ChevronDown, ChevronRight, Eye, Edit2 } from "lucide-react"
import systemPromptText from "@/data/systemPrompt.txt?raw"

interface ParametersTabProps {
  onProcessComplete: () => void
}

export function ParametersTab({ onProcessComplete }: ParametersTabProps) {
  const { worksheetId, questions, setQuestions, markAsProcessed } = useApp()
  const [model, setModel] = useState("google/gemini-flash-lite")
  const [maxTokens, setMaxTokens] = useState("7000")
  const [temperature, setTemperature] = useState("0.2")
  const [topP, setTopP] = useState("1")
  const [enableThinking, setEnableThinking] = useState(false)
  const [enableReasoning, setEnableReasoning] = useState(false)
  const [batchSize, setBatchSize] = useState("10")
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [showPrompt, setShowPrompt] = useState(false)
  const [isEditingPrompt, setIsEditingPrompt] = useState(false)
  const [systemPrompt, setSystemPrompt] = useState(systemPromptText)

  const handleProcess = async () => {
    setIsProcessing(true)
    setProgress(0)

    // Simulate progress
    const totalQuestions = Math.min(questions.length, parseInt(batchSize))
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= totalQuestions) {
          clearInterval(interval)
          return totalQuestions
        }
        return prev + 1
      })
    }, 500)

    // Wait for 5-7 seconds
    await new Promise((resolve) => setTimeout(resolve, 6000))

    // Update all questions with AI processing
    const updatedQuestions = questions.map((q) => ({
      ...q,
      ai_processed: true,
      ai_question_rewrite: q.question,
      ai_question_reason: "No changes needed.",
      ai_answer1_rewrite: q.answer1,
      ai_answer1_reason: "No changes needed.",
      ai_answer2_rewrite: q.answer2,
      ai_answer2_reason: "No changes needed.",
      ai_answer3_rewrite: q.answer3,
      ai_answer3_reason: "No changes needed.",
      ai_answer4_rewrite: q.answer4,
      ai_answer4_reason: "No changes needed.",
    }))

    setQuestions(updatedQuestions)
    markAsProcessed()
    setIsProcessing(false)
    onProcessComplete()
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>LLM Parameters</CardTitle>
        </CardHeader>
        <CardContent>
        {isProcessing && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="p-8">
              <div className="flex flex-col items-center gap-4">
                <Loader2 className="h-12 w-12 animate-spin text-primary" />
                <div className="text-center">
                  <div className="text-lg font-semibold">
                    Processing questions...
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {progress} / {Math.min(questions.length, parseInt(batchSize))}{" "}
                    questions processed
                  </div>
                  <div className="text-xs text-muted-foreground mt-2">
                    Please wait...
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <Label htmlFor="model">Model</Label>
              <Select value={model} onValueChange={setModel}>
                <SelectTrigger id="model">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="google/gemini-flash-lite">
                    Google Gemini Flash Lite
                  </SelectItem>
                  <SelectItem value="openai/gpt-4">OpenAI GPT-4</SelectItem>
                  <SelectItem value="anthropic/claude-3">
                    Anthropic Claude 3
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="maxTokens">Max Tokens</Label>
              <Input
                id="maxTokens"
                type="number"
                value={maxTokens}
                onChange={(e) => setMaxTokens(e.target.value)}
              />
            </div>

            <div>
              <Label htmlFor="temperature">Temperature</Label>
              <Input
                id="temperature"
                type="number"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(e.target.value)}
              />
            </div>

            <div>
              <Label htmlFor="topP">Top-P</Label>
              <Input
                id="topP"
                type="number"
                step="0.1"
                value={topP}
                onChange={(e) => setTopP(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <Label htmlFor="worksheet">Worksheet ID</Label>
              <Input id="worksheet" value={worksheetId} disabled />
            </div>

            <div>
              <Label htmlFor="batchSize">Batch Size</Label>
              <Input
                id="batchSize"
                type="number"
                value={batchSize}
                onChange={(e) => setBatchSize(e.target.value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="thinking">Enable Thinking</Label>
              <Switch
                id="thinking"
                checked={enableThinking}
                onCheckedChange={setEnableThinking}
              />
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="reasoning">Enable Reasoning</Label>
              <Switch
                id="reasoning"
                checked={enableReasoning}
                onCheckedChange={setEnableReasoning}
              />
            </div>

            <Button
              onClick={handleProcess}
              className="w-full mt-4"
              size="lg"
              disabled={isProcessing || questions.length === 0}
            >
              {isProcessing ? "Processing..." : "Process Questions"}
            </Button>

            {questions.length === 0 && (
              <p className="text-sm text-red-500 text-center">
                Please load questions from the Review tab first
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">System Prompt</CardTitle>
          <div className="flex gap-2">
            {showPrompt && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditingPrompt(!isEditingPrompt)}
              >
                {isEditingPrompt ? <Eye className="h-4 w-4 mr-2" /> : <Edit2 className="h-4 w-4 mr-2" />}
                {isEditingPrompt ? "View" : "Edit"}
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowPrompt(!showPrompt)}
            >
              {showPrompt ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
              {showPrompt ? "Collapse" : "Expand"}
            </Button>
          </div>
        </div>
      </CardHeader>
      {showPrompt && (
        <CardContent>
          {isEditingPrompt ? (
            <>
              <Textarea
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                className="min-h-[400px] font-mono text-xs"
              />
              <div className="flex justify-end gap-2 mt-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSystemPrompt(systemPromptText)
                    setIsEditingPrompt(false)
                  }}
                >
                  Reset to Default
                </Button>
                <Button
                  size="sm"
                  onClick={() => setIsEditingPrompt(false)}
                >
                  Save Changes
                </Button>
              </div>
            </>
          ) : (
            <pre className="bg-gray-50 p-4 rounded border text-xs overflow-x-auto whitespace-pre-wrap max-h-[400px] overflow-y-auto">
              {systemPrompt}
            </pre>
          )}
        </CardContent>
      )}
    </Card>
  </div>
  )
}
