'use client'

import { Settings, ChevronLeft, RefreshCw } from 'lucide-react'

export function MobileMockup() {
  return (
    <div className="relative w-[380px] h-[600px] bg-zinc-900 rounded-[40px] border-4 border-zinc-800 p-6 shadow-2xl">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1/3 h-6 bg-zinc-800 rounded-b-2xl" />
      
      <div className="flex justify-between items-center mb-8">
        <ChevronLeft className="w-6 h-6 text-gray-400" />
        <Settings className="w-6 h-6 text-gray-400" />
      </div>

      <div className="bg-zinc-800 rounded-xl p-4 mb-8">
        <div className="text-sm text-gray-400">Your Balance</div>
        <div className="flex items-center justify-between">
          <div className="text-2xl font-bold text-white">0.0032 ₿</div>
          <button className="p-2 bg-yellow-400 rounded-full">
            <RefreshCw className="w-5 h-5 text-black" />
          </button>
        </div>
      </div>

      <div className="relative aspect-square">
        <div className="absolute inset-0 rounded-full border-4 border-blue-500/20" />
        <div className="absolute inset-0 rounded-full border-4 border-blue-500 border-l-transparent transform -rotate-45" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-4xl font-bold text-white">12,334</div>
        </div>
      </div>
    </div>
  )
}

