import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ParametersTab } from "./ParametersTab"
import { DashboardTab } from "./DashboardTab"
import { APIDetailsTab } from "./APIDetailsTab"
import { APILogsTab } from "./APILogsTab"

export function LLMModule() {
  const [activeTab, setActiveTab] = useState("parameters")
  const [isProcessed, setIsProcessed] = useState(false)

  const handleProcessComplete = () => {
    setIsProcessed(true)
    setActiveTab("dashboard")
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">LLM Connection</h2>
        <p className="text-muted-foreground">
          Configure and run batch LLM processing on questions
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="parameters">Parameters</TabsTrigger>
          <TabsTrigger value="api-details" disabled={!isProcessed}>
            API Details
          </TabsTrigger>
          <TabsTrigger value="dashboard" disabled={!isProcessed}>
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="logs" disabled={!isProcessed}>
            API Logs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="parameters">
          <ParametersTab onProcessComplete={handleProcessComplete} />
        </TabsContent>

        <TabsContent value="api-details">
          <APIDetailsTab />
        </TabsContent>

        <TabsContent value="dashboard">
          <DashboardTab />
        </TabsContent>

        <TabsContent value="logs">
          <APILogsTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
