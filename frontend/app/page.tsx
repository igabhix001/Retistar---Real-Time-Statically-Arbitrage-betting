import { Nav } from '@/components/nav'
import { TrendingUp, BarChart2, Zap, Globe, Clock, ShieldCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-white text-black">
      <Nav />

      <div className="container mx-auto px-4">
        {/* Hero Section */}
        <div className="pt-32 pb-16">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center px-4 py-2 bg-gray-100 rounded-full mb-6">
              <Zap className="w-4 h-4 text-gray-600 mr-2" />
              <span className="text-sm text-gray-600">Live Arbitrage Detection</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold text-black leading-tight mb-6">
              Real-Time Statistical<br />
              <span className="text-gray-700">Arbitrage Betting</span>
            </h1>

            <p className="text-lg text-gray-600 mb-8">
              Leverage advanced algorithms and real-time statistical analysis to identify
              profitable arbitrage opportunities across multiple betting markets.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link href="/login">
                <Button size="lg" className="bg-gray-900 hover:bg-gray-700 text-white">
                  Sign In
                </Button>
              </Link>
              <Link href="/signup">
                <Button size="lg" variant="outline" className="border-gray-700 text-gray-700 hover:bg-gray-100">
                  Sign Up
                </Button>
              </Link>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-6 max-w-2xl mx-auto">
              <div className="flex items-center gap-2 justify-center">
                <Globe className="w-5 h-5 text-gray-700" />
                <span className="text-gray-600">Global Markets</span>
              </div>
              <div className="flex items-center gap-2 justify-center">
                <Clock className="w-5 h-5 text-gray-700" />
                <span className="text-gray-600">24/7 Trading</span>
              </div>
              <div className="flex items-center gap-2 justify-center">
                <ShieldCheck className="w-5 h-5 text-gray-700" />
                <span className="text-gray-600">Secure Platform</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}


