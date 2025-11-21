import { AppProvider, useApp } from "@/context/AppContext"
import { Layout } from "@/components/layout/Layout"
import { ReviewModule } from "@/components/review/ReviewModule"
import { LLMModule } from "@/components/llm/LLMModule"
import { BatchUpdateModule } from "@/components/batch/BatchUpdateModule"

function AppContent() {
  const { activeNav, setActiveNav } = useApp()

  return (
    <Layout activeNav={activeNav} onNavChange={setActiveNav}>
      {activeNav === 'review' && <ReviewModule />}
      {activeNav === 'llm' && <LLMModule />}
      {activeNav === 'batch' && <BatchUpdateModule />}
    </Layout>
  )
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  )
}

export default App
