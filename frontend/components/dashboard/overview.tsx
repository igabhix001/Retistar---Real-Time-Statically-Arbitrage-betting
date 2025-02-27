'use client'

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

const data = [
  { name: "20 Mar", Income: 42000, Expenses: 28000 },
  { name: "21 Mar", Income: 35000, Expenses: 25000 },
  { name: "22 Mar", Income: 45000, Expenses: 30000 },
  { name: "23 Mar", Income: 42500, Expenses: 25200 },
  { name: "24 Mar", Income: 38000, Expenses: 27800 },
  { name: "25 Mar", Income: 41000, Expenses: 28500 },
  { name: "26 Mar", Income: 43000, Expenses: 29000 },
]

export function Overview() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <defs>
          <linearGradient id="incomeGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.2}/>
            <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="expensesGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#F97316" stopOpacity={0.2}/>
            <stop offset="95%" stopColor="#F97316" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <XAxis 
          dataKey="name" 
          stroke="#888888" 
          fontSize={12} 
          tickLine={false} 
          axisLine={false}
          dy={10}
        />
        <YAxis
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => `${value/1000}K`}
          dx={-10}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: 'rgba(0,0,0,0.8)', 
            border: 'none',
            borderRadius: '8px',
            color: 'white'
          }}
        />
        <Line
          type="monotone"
          dataKey="Income"
          stroke="#8B5CF6"
          strokeWidth={2}
          dot={false}
          fill="url(#incomeGradient)"
        />
        <Line
          type="monotone"
          dataKey="Expenses"
          stroke="#F97316"
          strokeWidth={2}
          dot={false}
          fill="url(#expensesGradient)"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

