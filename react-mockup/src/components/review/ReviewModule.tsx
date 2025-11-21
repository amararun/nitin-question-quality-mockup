import { useState, useMemo } from "react"
import type { Question } from "@/types/index"
import { useApp } from "@/context/AppContext"
import { FilterPanel } from "./FilterPanel"
import { QuestionTable } from "./QuestionTable"
import { QuestionModal } from "./QuestionModal"
import mockQuestionsData from "@/data/mockQuestions.json"

export function ReviewModule() {
  const { worksheetId, setWorksheetId, questions, setQuestions, updateQuestion } = useApp()
  const [currentPage, setCurrentPage] = useState(1)
  const [reviewStatus, setReviewStatus] = useState("all")
  const [llmClassification, setLlmClassification] = useState("all")
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleRefresh = async () => {
    if (!worksheetId.trim()) {
      setQuestions([])
      return
    }

    // Simulate database fetch with loading state
    setIsLoading(true)
    
    // Simulate 5 second delay for "pulling data from database"
    await new Promise(resolve => setTimeout(resolve, 5000))

    // Filter mock questions by worksheet_id
    const filtered = (mockQuestionsData as any[]).filter(
      (q: any) => q.worksheet_id === worksheetId
    ) as Question[]
    setQuestions(filtered)
    setCurrentPage(1)
    setIsLoading(false)
  }

  // Apply filters
  const filteredQuestions = useMemo(() => {
    let filtered = questions

    if (reviewStatus !== "all") {
      filtered = filtered.filter((q) => q.review_status === reviewStatus)
    }

    if (llmClassification !== "all") {
      filtered = filtered.filter(
        (q) => q.review_classification === llmClassification
      )
    }

    return filtered
  }, [questions, reviewStatus, llmClassification])

  const handleExpandClick = (question: Question) => {
    setSelectedQuestion(question)
    setModalOpen(true)
  }

  const handleModalUpdate = (questionId: number, updates: Partial<Question>) => {
    updateQuestion(questionId, updates)
  }

  return (
    <div className="space-y-6">
      <FilterPanel
        worksheetId={worksheetId}
        reviewStatus={reviewStatus}
        llmClassification={llmClassification}
        isLoading={isLoading}
        onWorksheetIdChange={setWorksheetId}
        onReviewStatusChange={setReviewStatus}
        onLlmClassificationChange={setLlmClassification}
        onRefresh={handleRefresh}
      />

      <QuestionTable
        questions={filteredQuestions}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        onExpandClick={handleExpandClick}
      />

      <QuestionModal
        question={selectedQuestion}
        open={modalOpen}
        onOpenChange={setModalOpen}
        onUpdate={handleModalUpdate}
      />
    </div>
  )
}
