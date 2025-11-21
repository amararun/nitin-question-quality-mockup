import { cn } from "@/lib/utils"
import type { NavItem } from "@/types/index"

interface TopNavProps {
  activeNav: NavItem
  onNavChange: (nav: NavItem) => void
}

export function TopNav({ activeNav, onNavChange }: TopNavProps) {
  const navItems: { id: NavItem; label: string }[] = [
    { id: 'review', label: 'Review Questions' },
    { id: 'llm', label: 'LLM Connection' },
    { id: 'batch', label: 'Batch Update' },
  ]

  return (
    <nav className="border-b bg-white shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex h-20 items-center justify-between">
          <div className="flex items-center gap-3">
            <img
              src="/unicus_logo.png"
              alt="Unicus Olympiads"
              className="h-12"
            />
            <div className="border-l h-8 border-gray-300 mx-2"></div>
            <div className="font-semibold text-lg text-gray-700">Question Quality Assessment</div>
          </div>
          <div className="flex space-x-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onNavChange(item.id)}
                className={cn(
                  "relative px-4 py-2 text-sm font-medium transition-colors",
                  "hover:text-primary",
                  activeNav === item.id
                    ? "text-primary"
                    : "text-muted-foreground"
                )}
              >
                {item.label}
                {activeNav === item.id && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}
