"use client"
import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Menu, X } from 'lucide-react'

export function Nav() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen)

  return (
    <header className="fixed top-0 w-full z-50 bg-gradient-to-r from-purple-900 to-gray-900 border-b border-white/10">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex flex-col gap-1 ">
                <div className="flex items-center gap-2">
                  <img
                    src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/aaaaafff-KNjMQNb6R4c45ngdJCrZwiivU1yrRz.png"
                    alt="RETISTAR Logo"
                    className="h-10 md:h-10"
                  />
                </div>
                <span className="text-[0.6rem] text-gray-300 hidden md:block flex px-0">
                  REAL TIME STATISTICAL ARBITRAGE BETTING
                </span>
              </div>
            </Link>
          </div>

          <div className="hidden md:flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="secondary" className="bg-white text-black hover:bg-white/90">
              Dashboard
              </Button>
            </Link>
          </div>

          <div className="md:hidden">
            <button onClick={toggleMenu} className="text-white">
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="pt-4 pb-3 border-t border-gray-700">
            <div className="flex items-center px-5">
              <Link href="/dashboard" className="ml-4 block text-gray-300 hover:text-white transition">Dashboard</Link>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}

