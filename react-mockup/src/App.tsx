import { AppProvider, useApp } from "@/context/AppContext"
import { Layout } from "@/components/layout/Layout"
import { ReviewModule } from "@/components/review/ReviewModule"
import { LLMModule } from "@/components/llm/LLMModule"

function AppContent() {
  const { activeNav, setActiveNav } = useApp()

  return (
    <Layout activeNav={activeNav} onNavChange={setActiveNav}>
      {activeNav === 'review' && <ReviewModule />}
      {activeNav === 'llm' && <LLMModule />}
      {activeNav === 'batch' && (
        <div className="text-center text-muted-foreground py-12">
          Batch Update Module - Coming in Phase 4
        </div>
      )}
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
