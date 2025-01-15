export function SpendingLimits() {
  return (
    <div>
      <div className="mb-8">
        <h2 className="text-white font-medium mb-4">Spending Limits</h2>
        <div className="space-y-2">
          <div className="text-sm text-gray-400">
            <span className="text-white text-lg font-medium">180,000</span> USD used from 200,000
          </div>
          <div className="h-2 bg-purple-500/20 rounded-full">
            <div className="h-full w-[90%] bg-purple-500 rounded-full"></div>
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-white font-medium mb-4">Most spending categories</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/5 rounded-lg p-4">
            <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center mb-3">
              <span className="text-purple-500 text-2xl">🎓</span>
            </div>
            <div className="text-white mb-1">Education</div>
            <div className="text-sm text-gray-400">3,680.00 USD</div>
          </div>
          <div className="bg-white/5 rounded-lg p-4">
            <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center mb-3">
              <span className="text-purple-500 text-2xl">🛍️</span>
            </div>
            <div className="text-white mb-1">Shopping</div>
            <div className="text-sm text-gray-400">2,650.00 USD</div>
          </div>
        </div>
        <button className="w-full text-center text-sm text-purple-500 mt-4">
          See all ›
        </button>
      </div>
    </div>
  )
}

