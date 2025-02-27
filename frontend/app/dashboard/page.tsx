'use client'

import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Overview } from "@/components/dashboard/overview"
import { RecentTransactions } from "@/components/dashboard/recent-transactions"
import { DashboardSidebar } from "@/components/dashboard/sidebar"
import { MyCards } from "@/components/dashboard/my-cards"
import { SpendingLimits } from "@/components/dashboard/spending-limits"
import { Search, Bell, Settings, Copy, ChevronDown, Menu } from 'lucide-react'
import { SidebarProvider, SidebarTrigger, useSidebar } from "@/components/ui/sidebar"

export default function DashboardPage() {
  return (
    <SidebarProvider>
      <div className="min-h-screen bg-gradient-to-br from-purple-950 via-gray-900 to-black">
        <div className="flex">
          <DashboardSidebar />

          {/* Main Content */}
          <div className="flex-1 flex flex-col min-h-screen">
            {/* Top Bar */}
            <div className="bg-gradient-to-r from-purple-900 to-black border-b border-purple-700/30 p-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                  <SidebarTrigger>
                    <Button variant="ghost" size="icon" className="text-purple-300">
                      <Menu className="h-6 w-6" />
                    </Button>
                  </SidebarTrigger>
                  <span className="text-xl font-bold text-purple-300 md:text-2xl">DASHBOARD</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="relative hidden md:block">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-purple-300/70 h-4 w-4" />
                    <Input 
                      type="text" 
                      placeholder="Search" 
                      className="pl-10 w-64 bg-purple-900/30 border-purple-700/30 text-purple-300 placeholder:text-purple-300/50"
                    />
                  </div>
                  <Button variant="ghost" size="icon" className="text-purple-300">
                    <Bell className="h-5 w-5" />
                  </Button>
                  <div className="hidden md:flex items-center gap-2">
                    <img src="/placeholder.svg" alt="USD" className="w-6 h-6 rounded-full" />
                    <span className="text-purple-300">USD</span>
                    <ChevronDown className="h-4 w-4 text-purple-300/70" />
                  </div>
                  <div className="flex items-center gap-2">
                    <img src="/placeholder.svg" alt="Profile" className="w-8 h-8 rounded-full" />
                    <div className="hidden md:block text-sm">
                      <div className="text-purple-300">Hello Emily</div>
                      <div className="text-purple-300/70 text-xs">emilygething@gmail.com</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Dashboard Content */}
            <div className="flex-1 p-4 md:p-8 overflow-y-auto">
              <div className="flex flex-col lg:flex-row gap-8">
                {/* Main Column */}
                <div className="flex-1 space-y-6">
                  {/* Welcome Section */}
                  <div>
                    <h1 className="text-2xl text-purple-300">Welcome back</h1>
                    <h2 className="text-3xl font-bold text-purple-300">Emily</h2>
                    <p className="text-purple-300/70 text-sm">Last updated 05 Jan</p>
                  </div>

                  {/* Balance Card */}
                  <Card className="bg-purple-900/30 backdrop-blur-sm border-purple-700/30 p-4 md:p-6">
                    {/* Balance content */}
                    <Overview />
                  </Card>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Stats cards */}
                  </div>

                  {/* Recent Transactions */}
                  <div className="overflow-x-auto">
                    <RecentTransactions />
                  </div>
                </div>

                {/* Right Sidebar */}
                <div className="w-full lg:w-80 space-y-6">
                  <MyCards />
                  <SpendingLimits />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SidebarProvider>
  )
}

