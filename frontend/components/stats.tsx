import { TrendingUp, Users, BarChart2 } from 'lucide-react'

export function Stats() {
  return (
    <div className="grid md:grid-cols-3 gap-6 py-12">
      <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-10 h-10 rounded-lg bg-purple-600/20 flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-purple-400" />
          </div>
          <span className="text-2xl font-bold text-white">98.7%</span>
        </div>
        <div className="text-gray-400">Success Rate</div>
        <div className="mt-2 text-sm text-purple-400">+2.4% from last week</div>
      </div>

      <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-10 h-10 rounded-lg bg-purple-600/20 flex items-center justify-center">
            <Users className="w-5 h-5 text-purple-400" />
          </div>
          <span className="text-2xl font-bold text-white">12,234</span>
        </div>
        <div className="text-gray-400">Active Traders</div>
        <div className="mt-2 text-sm text-purple-400">+1,234 this month</div>
      </div>

      <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-10 h-10 rounded-lg bg-purple-600/20 flex items-center justify-center">
            <BarChart2 className="w-5 h-5 text-purple-400" />
          </div>
          <span className="text-2xl font-bold text-white">$4.2M</span>
        </div>
        <div className="text-gray-400">Total Volume</div>
        <div className="mt-2 text-sm text-purple-400">+12% this week</div>
      </div>
    </div>
  )
}

