'use client'

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import { ArrowRight, TrendingUp } from 'lucide-react'

type Opportunity = {
  id: number
  sport: string
  bookmaker1: string
  bookmaker2: string
  odds1: number
  odds2: number
  profit: number
  timestamp: Date
}

export function ArbitrageOpportunities() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([
    {
      id: 1,
      sport: "Football",
      bookmaker1: "Bookmaker A",
      bookmaker2: "Bookmaker B",
      odds1: 2.10,
      odds2: 1.95,
      profit: 2.8,
      timestamp: new Date()
    },
    {
      id: 2,
      sport: "Tennis",
      bookmaker1: "Bookmaker C",
      bookmaker2: "Bookmaker D",
      odds1: 1.85,
      odds2: 2.20,
      profit: 3.2,
      timestamp: new Date()
    },
    {
      id: 3,
      sport: "Basketball",
      bookmaker1: "Bookmaker B",
      bookmaker2: "Bookmaker E",
      odds1: 1.75,
      odds2: 2.35,
      profit: 2.5,
      timestamp: new Date()
    }
  ])

  useEffect(() => {
    const timer = setInterval(() => {
      // Simulate updating opportunities
      setOpportunities(prev => {
        const newOpps = [...prev]
        const randomIndex = Math.floor(Math.random() * newOpps.length)
        newOpps[randomIndex] = {
          ...newOpps[randomIndex],
          odds1: +(Math.random() * 0.1 + newOpps[randomIndex].odds1).toFixed(2),
          odds2: +(Math.random() * 0.1 + newOpps[randomIndex].odds2).toFixed(2),
          profit: +(Math.random() * 0.5 + newOpps[randomIndex].profit).toFixed(1),
          timestamp: new Date()
        }
        return newOpps
      })
    }, 3000)

    return () => clearInterval(timer)
  }, [])

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      {opportunities.map((opp) => (
        <Card 
          key={opp.id}
          className="bg-white/5 backdrop-blur-sm border-purple-500/20 hover:bg-white/10 transition-colors cursor-pointer group"
        >
          <div className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="text-sm text-gray-400">{opp.sport}</div>
                <div className="text-xl font-semibold text-white mt-1">
                  {opp.profit}% Return
                </div>
              </div>
              <div className="bg-green-500/20 text-green-400 text-sm px-2 py-1 rounded-full flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                Live
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <div className="text-gray-400">{opp.bookmaker1}</div>
                <div className="text-white font-medium">{opp.odds1}</div>
              </div>
              <div className="flex justify-between items-center">
                <div className="text-gray-400">{opp.bookmaker2}</div>
                <div className="text-white font-medium">{opp.odds2}</div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-white/10 flex justify-between items-center">
              <div className="text-sm text-gray-400">
                Updated {Math.floor((new Date().getTime() - opp.timestamp.getTime()) / 1000)}s ago
              </div>
              <ArrowRight className="w-5 h-5 text-purple-400 transform group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

