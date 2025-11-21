import type { Question } from "@/types/index"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Eye } from "lucide-react"

interface QuestionTableProps {
  questions: Question[]
  currentPage: number
  onPageChange: (page: number) => void
  onExpandClick: (question: Question) => void
}

const ITEMS_PER_PAGE = 10

export function QuestionTable({
  questions,
  currentPage,
  onPageChange,
  onExpandClick,
}: QuestionTableProps) {
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
  const endIndex = startIndex + ITEMS_PER_PAGE
  const currentQuestions = questions.slice(startIndex, endIndex)
  const totalPages = Math.ceil(questions.length / ITEMS_PER_PAGE)

  const stripHtml = (html: string) => {
    const div = document.createElement('div')
    div.innerHTML = html
    return div.textContent || div.innerText || ''
  }

  const truncate = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  const getStatusBadge = (question: Question) => {
    if (!question.ai_processed) {
      return <Badge variant="secondary">Not Processed</Badge>
    }
    if (question.review_status === 'approved') {
      return <Badge className="bg-green-600">Approved</Badge>
    }
    if (question.review_status === 'rejected') {
      return <Badge variant="destructive">Rejected</Badge>
    }
    return <Badge className="bg-yellow-600">Pending Review</Badge>
  }

  return (
    <div className="space-y-4">
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[100px]">Question ID</TableHead>
              <TableHead className="w-[150px]">Worksheet ID</TableHead>
              <TableHead>Question</TableHead>
              <TableHead className="w-[150px]">Status</TableHead>
              <TableHead className="w-[80px]">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {currentQuestions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  No questions found. Enter a worksheet ID and click Refresh.
                </TableCell>
              </TableRow>
            ) : (
              currentQuestions.map((question) => (
                <TableRow key={question.questionid} className="text-xs">
                  <TableCell className="font-mono">{question.questionid}</TableCell>
                  <TableCell className="font-mono">{question.worksheet_id}</TableCell>
                  <TableCell>{truncate(stripHtml(question.question), 100)}</TableCell>
                  <TableCell>{getStatusBadge(question)}</TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onExpandClick(question)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {questions.length > 0 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Showing {startIndex + 1} to {Math.min(endIndex, questions.length)} of{' '}
            {questions.length} questions
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <div className="flex items-center gap-2">
              <span className="text-sm">
                Page {currentPage} of {totalPages}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
