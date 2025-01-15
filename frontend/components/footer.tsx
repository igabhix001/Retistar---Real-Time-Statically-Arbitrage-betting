import Link from 'next/link'
import { Facebook, Twitter, Instagram } from 'lucide-react'

export function Footer() {
  return (
    <footer className="bg-zinc-900 text-gray-300 py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          <div>
            <h3 className="text-white text-lg font-semibold mb-4">Connect with us</h3>
            <div className="flex space-x-4">
              <Link href="#" className="hover:text-white">
                <Facebook size={24} />
              </Link>
              <Link href="#" className="hover:text-white">
                <Twitter size={24} />
              </Link>
              <Link href="#" className="hover:text-white">
                <Instagram size={24} />
              </Link>
            </div>
          </div>
          
          <div>
            <h3 className="text-white text-lg font-semibold mb-4">General</h3>
            <ul className="space-y-2">
              <li><Link href="/about" className="hover:text-white">About Us</Link></li>
              <li><Link href="/terms" className="hover:text-white">Terms and Conditions</Link></li>
              <li><Link href="/privacy" className="hover:text-white">Privacy Policy</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-white text-lg font-semibold mb-4">Sportsbook</h3>
            <ul className="space-y-2">
              <li><Link href="/sportsbook/football" className="hover:text-white">Football</Link></li>
              <li><Link href="/sportsbook/basketball" className="hover:text-white">Basketball</Link></li>
              <li><Link href="/sportsbook/tennis" className="hover:text-white">Tennis</Link></li>
              <li><Link href="/sportsbook/horse-racing" className="hover:text-white">Horse Racing</Link></li>
              <li><Link href="/sportsbook/dog-racing" className="hover:text-white">Dog Racing</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-white text-lg font-semibold mb-4">Contact Information</h3>
            <p>RETISTAR, Kingdom of Sports</p>
            <p className="mt-2">
              <a href="mailto:support@retistar.com" className="hover:text-white">support@retistar.com</a>
            </p>
            <p className="mt-2">
              <a href="#" className="hover:text-white">Contact Us</a>
            </p>
          </div>
          
          <div>
            <h3 className="text-white text-lg font-semibold mb-4">App Stores</h3>
            <div className="space-y-2">
              <a href="#" className="inline-block">
                <img src="/app-store-badge.svg" alt="Download on the App Store" className="h-10" />
              </a>
              <a href="#" className="inline-block">
                <img src="/google-play-badge.svg" alt="Get it on Google Play" className="h-10" />
              </a>
            </div>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t border-gray-700 text-center">
          <p>&copy; {new Date().getFullYear()} Retistar. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

