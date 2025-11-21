import { useState } from "react"
import type { Question } from "@/types/index"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"
import { CheckCircle2, XCircle, AlertTriangle, HelpCircle } from "lucide-react"

interface QuestionModalProps {
  question: Question | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onUpdate: (questionId: number, updates: Partial<Question>) => void
}

export function QuestionModal({
  question,
  open,
  onOpenChange,
  onUpdate,
}: QuestionModalProps) {
  const [classification, setClassification] = useState<string>(
    question?.review_classification || ""
  )
  const [finalQuestion, setFinalQuestion] = useState<string>(
    question?.ai_question_rewrite || question?.question || ""
  )

  if (!question) return null

  const handleClassificationClick = (type: string) => {
    setClassification(type)
  }

  const handleApprove = () => {
    onUpdate(question.questionid, {
      review_status: "approved",
      review_classification: classification as any,
      final_question: finalQuestion,
      human_reviewed: true,
    })
    onOpenChange(false)
  }

  const getCorrectAnswerLabel = (correctAnswer: string) => {
    const labels: Record<string, string> = {
      a: "A",
      b: "B",
      c: "C",
      d: "D",
      e: "E",
    }
    return labels[correctAnswer.toLowerCase()] || correctAnswer
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[90vw] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>
              Question ID: {question.questionid} | Worksheet: {question.worksheet_id}
            </span>
            {question.review_status && (
              <Badge
                className={cn(
                  question.review_status === "approved" && "bg-green-600",
                  question.review_status === "rejected" && "bg-red-600",
                  question.review_status === "pending" && "bg-yellow-600"
                )}
              >
                {question.review_status}
              </Badge>
            )}
          </DialogTitle>
        </DialogHeader>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Left Column - Original */}
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-sm mb-2 text-gray-700">
                Original Question
              </h3>
              <div
                className="p-4 bg-gray-50 rounded border text-sm"
                dangerouslySetInnerHTML={{ __html: question.question }}
              />
            </div>

            {question.questionImage && (
              <div>
                <h3 className="font-semibold text-sm mb-2 text-gray-700">Question Image</h3>
                <div className="p-4 bg-gray-100 rounded border text-sm text-gray-500">
                  [Image: {question.questionImage}]
                </div>
              </div>
            )}

            <div>
              <h3 className="font-semibold text-sm mb-2 text-gray-700">
                Answer Options
              </h3>
              <div className="space-y-2">
                {["answer1", "answer2", "answer3", "answer4", "answer5"].map(
                  (key, idx) => {
                    const answer = question[key as keyof Question] as string
                    if (!answer) return null
                    const label = String.fromCharCode(65 + idx) // A, B, C, D, E
                    const isCorrect =
                      getCorrectAnswerLabel(question.correctanswer) === label

                    return (
                      <div
                        key={key}
                        className={cn(
                          "p-3 rounded border text-sm",
                          isCorrect
                            ? "bg-green-50 border-green-300"
                            : "bg-white"
                        )}
                      >
                        <div className="flex items-start gap-2">
                          <span className="font-semibold">{label}:</span>
                          <div
                            dangerouslySetInnerHTML={{ __html: answer }}
                            className="flex-1"
                          />
                          {isCorrect && (
                            <Badge className="bg-green-600 text-xs">
                              Correct
                            </Badge>
                          )}
                        </div>
                      </div>
                    )
                  }
                )}
              </div>
            </div>

            {question.hint && (
              <div>
                <h3 className="font-semibold text-sm mb-2 text-gray-700">Hint</h3>
                <div
                  className="p-3 bg-blue-50 rounded border border-blue-200 text-sm"
                  dangerouslySetInnerHTML={{ __html: question.hint }}
                />
              </div>
            )}
          </div>

          {/* Right Column - AI Rewrite & Actions */}
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-sm mb-2 text-gray-700">
                LLM Assessment
              </h3>
              {question.ai_processed ? (
                <div className="space-y-3">
                  <div>
                    <div className="text-xs font-medium text-gray-500 mb-1">
                      Question Rewrite:
                    </div>
                    <div
                      className="p-3 bg-blue-50 rounded border text-sm"
                      dangerouslySetInnerHTML={{
                        __html: question.ai_question_rewrite || "No changes",
                      }}
                    />
                  </div>
                  <div>
                    <div className="text-xs font-medium text-gray-500 mb-1">
                      Reason:
                    </div>
                    <div className="p-3 bg-gray-50 rounded border text-sm">
                      {question.ai_question_reason || "N/A"}
                    </div>
                  </div>

                  {/* Answer Rewrites */}
                  {question.ai_answer1_rewrite && (
                    <div className="space-y-2">
                      <div className="text-xs font-medium text-gray-500">
                        Answer Corrections:
                      </div>
                      {["1", "2", "3", "4", "5"].map((num) => {
                        const rewriteKey =
                          `ai_answer${num}_rewrite` as keyof Question
                        const reasonKey =
                          `ai_answer${num}_reason` as keyof Question
                        const rewrite = question[rewriteKey] as string
                        if (!rewrite) return null

                        return (
                          <div key={num} className="text-xs">
                            <span className="font-medium">
                              Answer {String.fromCharCode(64 + parseInt(num))}:
                            </span>{" "}
                            <span
                              dangerouslySetInnerHTML={{ __html: rewrite }}
                            />
                            {question[reasonKey] && (
                              <div className="text-gray-500 ml-4">
                                → {question[reasonKey] as string}
                              </div>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-4 bg-gray-50 rounded border text-sm text-gray-500 text-center">
                  Not yet processed by LLM
                </div>
              )}
            </div>

            {/* Classification Buttons */}
            <div>
              <h3 className="font-semibold text-sm mb-2 text-gray-700">
                Classification
              </h3>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant={classification === "all_ok" ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleClassificationClick("all_ok")}
                  className={cn(
                    classification === "all_ok" && "bg-green-600 hover:bg-green-700"
                  )}
                >
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  All OK
                </Button>
                <Button
                  variant={classification === "mistake" ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleClassificationClick("mistake")}
                  className={cn(
                    classification === "mistake" && "bg-red-600 hover:bg-red-700"
                  )}
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Mistake
                </Button>
                <Button
                  variant={
                    classification === "hallucinated" ? "default" : "outline"
                  }
                  size="sm"
                  onClick={() => handleClassificationClick("hallucinated")}
                  className={cn(
                    classification === "hallucinated" &&
                      "bg-yellow-600 hover:bg-yellow-700"
                  )}
                >
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Hallucinated
                </Button>
                <Button
                  variant={classification === "other" ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleClassificationClick("other")}
                  className={cn(
                    classification === "other" && "bg-gray-600 hover:bg-gray-700"
                  )}
                >
                  <HelpCircle className="h-4 w-4 mr-2" />
                  Other
                </Button>
              </div>
            </div>

            {/* Final Version Editor */}
            <div>
              <h3 className="font-semibold text-sm mb-2 text-gray-700">
                Final Version (Editable)
              </h3>
              <Textarea
                value={finalQuestion}
                onChange={(e) => setFinalQuestion(e.target.value)}
                className="min-h-[120px] font-mono text-sm"
                placeholder="Edit the final version of the question here..."
              />
              <p className="text-xs text-gray-500 mt-1">
                This will be saved when you click Approve
              </p>
            </div>

            {/* Approve Button */}
            <Button
              onClick={handleApprove}
              className="w-full bg-green-600 hover:bg-green-700"
              size="lg"
              disabled={!classification}
            >
              <CheckCircle2 className="h-5 w-5 mr-2" />
              Approve & Save
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
