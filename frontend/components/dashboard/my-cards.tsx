export function MyCards() {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-white font-medium">My Cards</h2>
        <button className="text-sm text-purple-500 flex items-center gap-1">
          Add Card <span className="text-lg">+</span>
        </button>
      </div>
      
      <div className="relative">
        <button className="absolute top-1/2 -left-4 transform -translate-y-1/2 text-white text-2xl">
          ‹
        </button>
        <div className="bg-gradient-to-br from-purple-600 via-purple-700 to-purple-800 rounded-xl p-6 text-white">
          <div className="flex justify-between items-start mb-8">
            <span>Transfer Card</span>
            <img src="/mastercard-logo.svg" alt="Mastercard" className="h-8" />
          </div>
          <div className="mb-4">
            <h3 className="text-lg font-medium">Emily Watson</h3>
            <div className="text-lg tracking-wider">•••• •••• •••• 1210</div>
          </div>
          <div className="text-sm">Exp 10/25</div>
        </div>
        <button className="absolute top-1/2 -right-4 transform -translate-y-1/2 text-white text-2xl">
          ›
        </button>
      </div>

      <div className="mt-6">
        <div className="flex justify-between items-center mb-4">
          <span className="text-gray-400">Balance</span>
          <div>
            <span className="text-2xl font-bold text-white">36,475.40</span>
            <span className="text-gray-400 ml-1">USD</span>
          </div>
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                <span className="text-purple-500 text-xl">⚡</span>
              </div>
              <div>
                <div className="text-white">Electricity bills</div>
                <div className="text-xs text-gray-400">See info ›</div>
              </div>
            </div>
            <span className="text-white">-140 USD</span>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                <span className="text-blue-500 text-xl">↑</span>
              </div>
              <div>
                <div className="text-white">Transfer</div>
                <div className="text-xs text-gray-400">See info ›</div>
              </div>
            </div>
            <span className="text-white">-174 USD</span>
          </div>
        </div>
      </div>
    </div>
  )
}

