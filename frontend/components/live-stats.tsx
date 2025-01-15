'use client'

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'

export function LiveStats() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [activeUsers, setActiveUsers] = useState(1234)
  const [opportunities, setOpportunities] = useState(42)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
      // Simulate live user count changes
      setActiveUsers(prev => prev + Math.floor(Math.random() * 3) - 1)
      // Simulate opportunity count changes
      setOpportunities(prev => Math.max(30, Math.min(50, prev + Math.floor(Math.random() * 3) - 1)))
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  return (
    <div className="relative">
      {/* Background gradient effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-blue-600/20 rounded-3xl blur-3xl" />
      
      <Card className="relative bg-black/50 backdrop-blur-xl border-purple-500/20 rounded-3xl overflow-hidden">
        <div className="p-6">
          <div className="flex justify-between items-center mb-8">
            <div className="text-purple-400">Live Statistics</div>
            <div className="text-gray-400 tabular-nums">
              {currentTime.toLocaleTimeString()}
            </div>
          </div>

          <div className="space-y-6">
            <div>
              <div className="text-gray-400 mb-2">Active Traders</div>
              <div className="text-3xl font-bold text-white tabular-nums">
                {activeUsers.toLocaleString()}
              </div>
              <div className="h-2 bg-purple-900/30 rounded-full mt-2">
                <div 
                  className="h-full bg-purple-500 rounded-full transition-all duration-500"
                  style={{ width: `${(activeUsers % 100) + 50}%` }}
                />
              </div>
            </div>

            <div>
              <div className="text-gray-400 mb-2">Current Opportunities</div>
              <div className="text-3xl font-bold text-white tabular-nums">
                {opportunities}
              </div>
              <div className="h-2 bg-purple-900/30 rounded-full mt-2">
                <div 
                  className="h-full bg-purple-500 rounded-full transition-all duration-500"
                  style={{ width: `${(opportunities / 50) * 100}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-purple-900/20 rounded-xl p-4">
                <div className="text-purple-400 text-sm mb-1">Win Rate</div>
                <div className="text-2xl font-bold text-white">98.2%</div>
              </div>
              <div className="bg-purple-900/20 rounded-xl p-4">
                <div className="text-purple-400 text-sm mb-1">Avg. Return</div>
                <div className="text-2xl font-bold text-white">3.4%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Animated dots */}
        <div className="absolute top-4 right-4 flex gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse delay-100" />
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse delay-200" />
        </div>
      </Card>
    </div>
  )
}

