import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import {
  CheckCircle2,
  XCircle,
  Download,
  Copy,
  RotateCcw,
} from "lucide-react"
import { mockValidationReport } from "@/data/mockValidation"

export function ValidationReport() {
  const [isRollingBack, setIsRollingBack] = useState(false)
  const [rollbackComplete, setRollbackComplete] = useState(false)
  const report = mockValidationReport

  const handleDownloadPDF = () => {
    alert("Downloading validation report as PDF...")
  }

  const handleCopyCSV = () => {
    const csvData = `Records Summary
Total Records,${report.summary.total_records}
Updated Records,${report.summary.updated_records}
Failed Records,${report.summary.failed_records}
Duration,${report.summary.duration_seconds}s

Performance Metrics
Total Time,${report.performance.total_time_seconds}s
Avg Time per Record,${report.performance.avg_time_per_record_ms}ms
Throughput,${report.performance.throughput_records_per_second} records/s`

    navigator.clipboard.writeText(csvData)
    alert("Validation data copied to clipboard!")
  }

  const handleRollback = async () => {
    const confirmed = confirm(
      "Are you sure you want to rollback? This will restore the database to its pre-update state."
    )
    if (!confirmed) return

    setIsRollingBack(true)
    await new Promise((resolve) => setTimeout(resolve, 10000)) // 10 seconds
    setIsRollingBack(false)
    setRollbackComplete(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">
            Database Update Validation Report
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Generated on {new Date().toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleDownloadPDF}>
            <Download className="h-4 w-4 mr-2" />
            Download PDF
          </Button>
          <Button variant="outline" size="sm" onClick={handleCopyCSV}>
            <Copy className="h-4 w-4 mr-2" />
            Copy CSV
          </Button>
        </div>
      </div>

      {/* Section 1: Records Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Records Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Total Records</p>
              <p className="text-2xl font-bold">
                {report.summary.total_records}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">
                Successfully Updated
              </p>
              <p className="text-2xl font-bold text-green-600">
                {report.summary.updated_records}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Failed</p>
              <p className="text-2xl font-bold text-red-600">
                {report.summary.failed_records}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Start Time</p>
              <p className="text-sm font-mono">{report.summary.start_time}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">End Time</p>
              <p className="text-sm font-mono">{report.summary.end_time}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Duration</p>
              <p className="text-sm font-semibold">
                {report.summary.duration_seconds} seconds
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section 2: Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Performance Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Metric</TableHead>
                <TableHead className="text-right">Value</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell>Total Time</TableCell>
                <TableCell className="text-right font-mono">
                  {report.performance.total_time_seconds}s
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Avg Time per Record</TableCell>
                <TableCell className="text-right font-mono">
                  {report.performance.avg_time_per_record_ms}ms
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Throughput</TableCell>
                <TableCell className="text-right font-mono">
                  {report.performance.throughput_records_per_second} records/s
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Section 3: Error Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            Error Breakdown ({report.errors.count} errors)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {report.errors.count > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Error Type</TableHead>
                  <TableHead>Count</TableHead>
                  <TableHead>Sample Question IDs</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {report.errors.breakdown.map((error, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="font-medium">
                      {error.error_type}
                    </TableCell>
                    <TableCell>
                      <Badge variant="destructive">{error.count}</Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {error.sample_questionids.join(", ")}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle2 className="h-5 w-5" />
              <span>No errors encountered</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Section 4: Data Integrity Validation */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Data Integrity Validation</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">
                Pre-Update Record Count
              </p>
              <p className="text-lg font-mono">
                {report.validation.pre_update_count.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">
                Post-Update Record Count
              </p>
              <p className="text-lg font-mono">
                {report.validation.post_update_count.toLocaleString()}
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm">Data Integrity Check</span>
              {report.validation.data_integrity_check === "passed" ? (
                <Badge className="bg-green-600">
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  Passed
                </Badge>
              ) : (
                <Badge variant="destructive">
                  <XCircle className="h-3 w-3 mr-1" />
                  Failed
                </Badge>
              )}
            </div>
            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm">Foreign Key Violations</span>
              <span className="font-mono text-sm">
                {report.validation.foreign_key_violations}
              </span>
            </div>
            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm">Null Constraint Violations</span>
              <span className="font-mono text-sm">
                {report.validation.null_constraint_violations}
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm">Unmodified Column Checksums</span>
              <Badge className="bg-green-600">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                Match
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section 5: Rollback Information */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Rollback Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Backup Available</p>
              <div className="flex items-center gap-2 mt-1">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span className="font-semibold">Yes</span>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">
                Rollback Available
              </p>
              <div className="flex items-center gap-2 mt-1">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span className="font-semibold">Yes</span>
              </div>
            </div>
          </div>

          <div>
            <p className="text-sm text-muted-foreground">Backup Location</p>
            <p className="font-mono text-sm bg-gray-100 p-2 rounded mt-1">
              {report.backup_location}
            </p>
          </div>

          {rollbackComplete ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-semibold text-green-900">
                    ✓ Rollback Complete
                  </p>
                  <p className="text-sm text-green-700 mt-1">
                    Original database state has been restored from backup.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <Button
              variant="destructive"
              onClick={handleRollback}
              disabled={isRollingBack}
              className="w-full"
            >
              {isRollingBack ? (
                <>
                  <RotateCcw className="mr-2 h-4 w-4 animate-spin" />
                  Rolling back... Please wait
                </>
              ) : (
                <>
                  <RotateCcw className="mr-2 h-4 w-4" />
                  Rollback to Previous State
                </>
              )}
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Section 6: Additional Validation Checks */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            Additional Validation Checks
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm">HTML Tags Balanced</span>
              <Badge className="bg-green-600">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                Passed
              </Badge>
            </div>
            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm">Character Encoding</span>
              <Badge className="bg-green-600">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                Passed
              </Badge>
            </div>
            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm">Field Length Limits</span>
              <Badge className="bg-green-600">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                Passed
              </Badge>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm">Referential Integrity</span>
              <Badge className="bg-green-600">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                Passed
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

