import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { RefreshCw } from "lucide-react"

interface FilterPanelProps {
  worksheetId: string
  reviewStatus: string
  llmClassification: string
  onWorksheetIdChange: (id: string) => void
  onReviewStatusChange: (status: string) => void
  onLlmClassificationChange: (classification: string) => void
  onRefresh: () => void
}

export function FilterPanel({
  worksheetId,
  reviewStatus,
  llmClassification,
  onWorksheetIdChange,
  onReviewStatusChange,
  onLlmClassificationChange,
  onRefresh,
}: FilterPanelProps) {
  return (
    <Card className="bg-gray-50">
      <CardContent className="pt-6">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="text-sm font-medium mb-2 block">
              Worksheet ID
            </label>
            <Input
              placeholder="e.g., S09TISNID12"
              value={worksheetId}
              onChange={(e) => onWorksheetIdChange(e.target.value)}
            />
          </div>

          <div className="w-[180px]">
            <label className="text-sm font-medium mb-2 block">
              Review Status
            </label>
            <Select value={reviewStatus} onValueChange={onReviewStatusChange}>
              <SelectTrigger>
                <SelectValue placeholder="All" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="w-[180px]">
            <label className="text-sm font-medium mb-2 block">
              LLM Classification
            </label>
            <Select
              value={llmClassification}
              onValueChange={onLlmClassificationChange}
            >
              <SelectTrigger>
                <SelectValue placeholder="All" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="all_ok">All OK</SelectItem>
                <SelectItem value="mistake">Mistake</SelectItem>
                <SelectItem value="hallucinated">Hallucinated</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button onClick={onRefresh} className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
