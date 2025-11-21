import { createContext, useContext, useState, useEffect } from "react"
import type { ReactNode } from "react"
import type { Question, NavItem } from "@/types/index"

interface AppContextType {
  worksheetId: string
  activeNav: NavItem
  processedState: boolean
  questions: Question[]
  setWorksheetId: (id: string) => void
  setActiveNav: (nav: NavItem) => void
  markAsProcessed: () => void
  setQuestions: (questions: Question[]) => void
  updateQuestion: (questionId: number, updates: Partial<Question>) => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  const [worksheetId, setWorksheetIdState] = useState<string>(() => {
    return localStorage.getItem('worksheetId') || 'S09ATOTAN12'
  })
  const [activeNav, setActiveNavState] = useState<NavItem>(() => {
    return (localStorage.getItem('activeNav') as NavItem) || 'review'
  })
  const [processedState, setProcessedState] = useState<boolean>(() => {
    return localStorage.getItem('processedState') === 'true'
  })
  const [questions, setQuestionsState] = useState<Question[]>(() => {
    const saved = localStorage.getItem('questions')
    return saved ? JSON.parse(saved) : []
  })

  // Persist to localStorage
  useEffect(() => {
    localStorage.setItem('worksheetId', worksheetId)
  }, [worksheetId])

  useEffect(() => {
    localStorage.setItem('activeNav', activeNav)
  }, [activeNav])

  useEffect(() => {
    localStorage.setItem('processedState', String(processedState))
  }, [processedState])

  useEffect(() => {
    localStorage.setItem('questions', JSON.stringify(questions))
  }, [questions])

  const setWorksheetId = (id: string) => {
    setWorksheetIdState(id)
  }

  const setActiveNav = (nav: NavItem) => {
    setActiveNavState(nav)
  }

  const markAsProcessed = () => {
    setProcessedState(true)
  }

  const setQuestions = (newQuestions: Question[]) => {
    setQuestionsState(newQuestions)
  }

  const updateQuestion = (questionId: number, updates: Partial<Question>) => {
    setQuestionsState(prev =>
      prev.map(q => q.questionid === questionId ? { ...q, ...updates } : q)
    )
  }

  return (
    <AppContext.Provider
      value={{
        worksheetId,
        activeNav,
        processedState,
        questions,
        setWorksheetId,
        setActiveNav,
        markAsProcessed,
        setQuestions,
        updateQuestion,
      }}
    >
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}
