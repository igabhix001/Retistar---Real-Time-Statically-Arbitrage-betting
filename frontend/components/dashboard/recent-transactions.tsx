import { Search } from 'lucide-react'
import { Input } from "@/components/ui/input"

const transactions = [
  {
    id: 1,
    name: "John Micheal",
    date: "Apr 20, 2024",
    time: "8:00 am",
    type: "Transfer",
    status: "Success",
    amount: "1200 USD"
  },
  {
    id: 2,
    name: "Emily",
    date: "Apr 24, 2024",
    time: "1:00 pm",
    type: "Transfer",
    status: "Failed",
    amount: "1200 USD"
  },
  {
    id: 3,
    name: "Emma",
    date: "Apr 27, 2024",
    time: "4:00 pm",
    type: "Transfer",
    status: "Success",
    amount: "1200 USD"
  }
]

export function RecentTransactions() {
  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-white font-medium">Recent Transactions</h2>
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input 
            type="text" 
            placeholder="Search transaction" 
            className="pl-10 bg-white/5 border-none text-white placeholder:text-gray-400"
          />
        </div>
      </div>

      <table className="w-full">
        <thead>
          <tr className="text-left text-gray-400 text-sm">
            <th className="pb-4">Name</th>
            <th className="pb-4">Date</th>
            <th className="pb-4">Type</th>
            <th className="pb-4">Status</th>
            <th className="pb-4">Amount</th>
            <th className="pb-4"></th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => (
            <tr key={transaction.id} className="border-t border-white/10">
              <td className="py-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-gray-500"></div>
                  <span className="text-white">{transaction.name}</span>
                </div>
              </td>
              <td className="text-gray-400">
                <div>{transaction.date}</div>
                <div className="text-sm">{transaction.time}</div>
              </td>
              <td className="text-white">{transaction.type}</td>
              <td>
                <span className={`px-2 py-1 rounded-full text-xs ${
                  transaction.status === 'Success' 
                    ? 'bg-green-500/20 text-green-500' 
                    : 'bg-red-500/20 text-red-500'
                }`}>
                  {transaction.status}
                </span>
              </td>
              <td className="text-white">{transaction.amount}</td>
              <td className="text-gray-400">•••</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

