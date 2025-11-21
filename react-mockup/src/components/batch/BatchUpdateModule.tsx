import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { useApp } from "@/context/AppContext"
import { ValidationReport } from "./ValidationReport"
import { AlertTriangle, CheckCircle2, Loader2 } from "lucide-react"

export function BatchUpdateModule() {
  const { worksheetId, questions } = useApp()
  const [isUpdating, setIsUpdating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentRecord, setCurrentRecord] = useState(0)
  const [updateComplete, setUpdateComplete] = useState(false)
  const [showReport, setShowReport] = useState(false)

  const approvedQuestions = questions.filter(
    (q) => q.review_status === "approved"
  )
  const totalApproved = approvedQuestions.length

  const handleUpdateDatabase = async () => {
    setIsUpdating(true)
    setProgress(0)
    setCurrentRecord(0)
    setUpdateComplete(false)
    setShowReport(false)

    // Simulate progress over 5 seconds
    const totalTime = 5000 // 5 seconds
    const steps = totalApproved
    const timePerStep = totalTime / steps

    for (let i = 0; i <= steps; i++) {
      await new Promise((resolve) => setTimeout(resolve, timePerStep))
      setProgress((i / steps) * 100)
      setCurrentRecord(i)
    }

    setIsUpdating(false)
    setUpdateComplete(true)
    setShowReport(true)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Batch Database Update</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="worksheetId">Worksheet ID</Label>
            <Input
              id="worksheetId"
              value={worksheetId}
              disabled
              className="font-mono"
            />
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <p className="font-semibold text-blue-900">
                  {totalApproved} approved questions ready for update
                </p>
                <p className="text-sm text-blue-700 mt-1">
                  Only questions with "Approved" status will be updated in the
                  production database.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <p className="font-semibold text-yellow-900">
                  Warning: Production Database Update
                </p>
                <p className="text-sm text-yellow-700 mt-1">
                  This will update live data. Ensure all approvals are correct.
                  A backup will be created automatically before updating.
                </p>
              </div>
            </div>
          </div>

          {isUpdating && (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">
                  Updating {currentRecord} of {totalApproved} records...
                </span>
                <span className="text-muted-foreground">
                  {progress.toFixed(0)}%
                </span>
              </div>
              <Progress value={progress} className="h-3" />
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Please wait while the database is being updated...</span>
              </div>
            </div>
          )}

          {updateComplete && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-semibold text-green-900">
                    ✓ Update Complete
                  </p>
                  <p className="text-sm text-green-700 mt-1">
                    Database update completed successfully. See validation
                    report below.
                  </p>
                </div>
              </div>
            </div>
          )}

          <Button
            onClick={handleUpdateDatabase}
            disabled={isUpdating || totalApproved === 0}
            className="w-full"
            size="lg"
          >
            {isUpdating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Updating Database...
              </>
            ) : (
              "Update Production Database"
            )}
          </Button>

          {totalApproved === 0 && (
            <p className="text-sm text-muted-foreground text-center">
              No approved questions to update. Please approve questions in the
              Review module first.
            </p>
          )}
        </CardContent>
      </Card>

      {showReport && <ValidationReport />}
    </div>
  )
}

