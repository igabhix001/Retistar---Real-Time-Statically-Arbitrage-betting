import { Nav } from '@/components/nav'
import { Stats } from '@/components/stats'
import { ArbitrageOpportunities } from '@/components/arbitrage-opportunities'
import { TrendingUp, BarChart2, Zap, Globe, Clock, ShieldCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-zinc-900 via-purple-900 to-black">
      <Nav />
      
      <div className="container mx-auto px-4">
        {/* Hero Section */}
        <div className="pt-32 pb-16">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center px-4 py-2 bg-purple-900/50 rounded-full mb-6">
              <Zap className="w-4 h-4 text-purple-400 mr-2" />
              <span className="text-sm text-purple-300">Live Arbitrage Detection</span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight mb-6">
              Real-Time Statistical<br />
              <span className="text-purple-400">Arbitrage Betting</span>
            </h1>
            
            <p className="text-lg text-gray-300 mb-8">
              Leverage advanced algorithms and real-time statistical analysis to identify 
              profitable arbitrage opportunities across multiple betting markets.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link href="/login">
              <Button size="lg" className="bg-purple-600 hover:bg-purple-700 text-white">
                Get Started
              </Button>
              </Link>
              <Link href="/signup">
              <Button size="lg" variant="outline" className="border-purple-600 text-purple-400 hover:bg-purple-600/10">
                Sign Up
              </Button>
              </Link>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-6 max-w-2xl mx-auto">
              <div className="flex items-center gap-2 justify-center">
                <Globe className="w-5 h-5 text-purple-400" />
                <span className="text-gray-300">Global Markets</span>
              </div>
              <div className="flex items-center gap-2 justify-center">
                <Clock className="w-5 h-5 text-purple-400" />
                <span className="text-gray-300">24/7 Trading</span>
              </div>
              <div className="flex items-center gap-2 justify-center">
                <ShieldCheck className="w-5 h-5 text-purple-400" />
                <span className="text-gray-300">Secure Platform</span>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <Stats />

        {/* Features Section */}
        <div className="py-16">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Advanced Statistical Analysis
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6">
              <div className="w-12 h-12 bg-purple-600/20 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Real-Time Tracking</h3>
              <p className="text-gray-400">
                Monitor odds movements and market changes across multiple bookmakers in real-time.
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6">
              <div className="w-12 h-12 bg-purple-600/20 rounded-lg flex items-center justify-center mb-4">
                <BarChart2 className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Statistical Edge</h3>
              <p className="text-gray-400">
                Utilize advanced algorithms to identify profitable arbitrage opportunities.
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6">
              <div className="w-12 h-12 bg-purple-600/20 rounded-lg flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Instant Execution</h3>
              <p className="text-gray-400">
                Execute trades quickly with our automated betting system and API integrations.
              </p>
            </div>
          </div>
        </div>

        {/* Live Opportunities Section */}
        <div className="py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">
              Live Arbitrage Opportunities
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Track real-time arbitrage opportunities across multiple bookmakers and markets.
            </p>
          </div>
          
          <ArbitrageOpportunities />
        </div>
      </div>
    </main>
  )
}

