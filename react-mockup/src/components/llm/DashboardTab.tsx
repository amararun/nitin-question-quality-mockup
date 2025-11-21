import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useApp } from "@/context/AppContext"
import { BarChart3, DollarSign, Clock, CheckCircle2 } from "lucide-react"

export function DashboardTab() {
  const { questions } = useApp()

  const totalQuestions = questions.length
  const processedQuestions = questions.filter((q) => q.ai_processed).length
  const changeRate = ((processedQuestions / totalQuestions) * 100).toFixed(1)
  const totalCost = (processedQuestions * 0.001228).toFixed(4)
  const totalTime = processedQuestions * 4.675

  return (
    <div className="space-y-6">
      {/* Metric Cards */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Questions
            </CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{processedQuestions}</div>
            <p className="text-xs text-muted-foreground">
              {totalQuestions} loaded
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Change Rate</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{changeRate}%</div>
            <p className="text-xs text-muted-foreground">
              Questions with changes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalCost}</div>
            <p className="text-xs text-muted-foreground">USD</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(totalTime)}s</div>
            <p className="text-xs text-muted-foreground">Processing time</p>
          </CardContent>
        </Card>
      </div>

      {/* Breakdown Tables */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Token Usage</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Input:</span>
              <span className="font-medium">
                {(processedQuestions * 3000).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Output:</span>
              <span className="font-medium">
                {(processedQuestions * 500).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between border-t pt-2">
              <span className="font-medium">Total:</span>
              <span className="font-bold">
                {(processedQuestions * 3500).toLocaleString()}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Cost Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Input tokens:</span>
              <span className="font-medium">
                ${((processedQuestions * 3000 * 0.075) / 1000000).toFixed(4)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Output tokens:</span>
              <span className="font-medium">
                ${((processedQuestions * 500 * 0.3) / 1000000).toFixed(4)}
              </span>
            </div>
            <div className="flex justify-between border-t pt-2">
              <span className="font-medium">Total:</span>
              <span className="font-bold">${totalCost}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Avg time/question:</span>
              <span className="font-medium">4.7s</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Throughput:</span>
              <span className="font-medium">12.8 q/min</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">API calls:</span>
              <span className="font-medium">
                {Math.ceil(processedQuestions / 10)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
