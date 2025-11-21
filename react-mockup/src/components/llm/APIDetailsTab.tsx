import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useApp } from "@/context/AppContext"

export function APIDetailsTab() {
  const { questions } = useApp()
  const processedQuestions = questions.filter((q) => q.ai_processed).length

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>API Call Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3">Request Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Model:</span>
                  <span className="font-medium">Google Gemini Flash Lite</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Questions Processed:</span>
                  <span className="font-medium">{processedQuestions}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Batch Size:</span>
                  <span className="font-medium">10</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">API Calls:</span>
                  <span className="font-medium">{Math.ceil(processedQuestions / 10)}</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-3">Resource Usage</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Tokens:</span>
                  <span className="font-medium">{(processedQuestions * 3500).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Input Tokens:</span>
                  <span className="font-medium">{(processedQuestions * 3000).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Output Tokens:</span>
                  <span className="font-medium">{(processedQuestions * 500).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Cost:</span>
                  <span className="font-medium">${(processedQuestions * 0.001228).toFixed(4)}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="border-t pt-4">
            <h3 className="font-semibold mb-3">Timing</h3>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-muted-foreground">Total Time</div>
                <div className="text-lg font-medium">{Math.round(processedQuestions * 4.675)}s</div>
              </div>
              <div>
                <div className="text-muted-foreground">Avg per Question</div>
                <div className="text-lg font-medium">4.7s</div>
              </div>
              <div>
                <div className="text-muted-foreground">Avg per API Call</div>
                <div className="text-lg font-medium">23.4s</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
