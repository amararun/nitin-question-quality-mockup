import { ReactNode } from "react"
import { TopNav } from "./TopNav"
import type { NavItem } from "@/types/index"

interface LayoutProps {
  children: ReactNode
  activeNav: NavItem
  onNavChange: (nav: NavItem) => void
}

export function Layout({ children, activeNav, onNavChange }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <TopNav activeNav={activeNav} onNavChange={onNavChange} />
      <main className="container mx-auto px-4 py-6 flex-1">
        {children}
      </main>
      <footer className="bg-white border-t mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-center text-sm text-gray-600">
            <span className="font-medium">Unicus Olympiads</span>
            <span className="mx-2">|</span>
            <span>B-1003, BPTP Freedom Park, Sector-57, Gurgaon, Haryana-122003, India</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
