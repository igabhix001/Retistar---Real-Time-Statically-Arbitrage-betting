'use client'

import Link from 'next/link'
import { LayoutDashboard, Wallet, RefreshCcw, Settings, ChevronLeft, ChevronRight } from 'lucide-react'
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"

export function DashboardSidebar() {
  const { toggleSidebar, open } = useSidebar()

  return (
    <Sidebar className="bg-gradient-to-b from-purple-900 via-purple-800 to-black border-r border-purple-700/30">
      <SidebarHeader className="p-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-purple-700/30 flex items-center justify-center">
            <span className="text-purple-300">F</span>
          </div>
          <span className="text-purple-300 font-bold">FINANCE</span>
        </div>
        <Button variant="ghost" size="icon" onClick={toggleSidebar} className="text-purple-300">
          {open ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </Button>
      </SidebarHeader>
      <SidebarContent>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild isActive>
              <Link href="/dashboard" className="flex items-center gap-3 text-purple-300">
                <LayoutDashboard className="w-5 h-5" />
                <span>Dashboard</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/balances" className="flex items-center gap-3 text-purple-300/70 hover:text-purple-300 transition-colors">
                <Wallet className="w-5 h-5" />
                <span>Balances</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/transactions" className="flex items-center gap-3 text-purple-300/70 hover:text-purple-300 transition-colors">
                <RefreshCcw className="w-5 h-5" />
                <span>Transactions</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
          
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/settings" className="flex items-center gap-3 text-purple-300/70 hover:text-purple-300 transition-colors">
                <Settings className="w-5 h-5" />
                <span>Settings</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarContent>

      <div className="mt-auto p-4">
        <div className="bg-purple-700/20 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center">
              <span className="text-purple-300">↑</span>
            </div>
            <span className="text-xs text-purple-300">New</span>
          </div>
          <h3 className="text-purple-300 font-medium mb-1">New update available</h3>
          <p className="text-sm text-purple-300/70 mb-3">Click to Update</p>
          <button className="w-full bg-purple-600 text-purple-100 rounded-lg py-2 text-sm hover:bg-purple-700 transition-colors">
            Update
          </button>
        </div>
      </div>
    </Sidebar>
  )
}

