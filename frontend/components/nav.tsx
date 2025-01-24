"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation"; // Correct hook for client-side navigation
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";

export function Nav() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  // Check session status from the backend
  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/auth/check-session",
          {
            method: "GET",
            credentials: "include", // Ensures cookies are sent with the request
          }
        );

        if (response.ok) {
          const data = await response.json();
          setIsLoggedIn(data.authenticated); // Update login state based on the response
        } else {
          setIsLoggedIn(false); // If the response is not ok, assume not logged in
        }
      } catch (error) {
        console.error("Error checking session:", error);
        setIsLoggedIn(false); // Handle errors gracefully
      }
    };

    checkSession();
  }, []); // Only runs once after initial mount

  const handleLogout = async () => {
    try {
      const response = await fetch("http://localhost:8000/auth/logout", {
        method: "POST",
        credentials: "include", // Include cookies in the request
      });

      if (response.ok) {
        setIsLoggedIn(false); // Update the state to logged out
        router.push("/"); // Redirect to the homepage
      } else {
        console.error("Failed to log out");
      }
    } catch (error) {
      console.error("Error during logout:", error);
    }
  };

  return (
    <header className="fixed top-0 w-full z-50 bg-white backdrop-blur text-black border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <img
                    src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/aaaaafff-KNjMQNb6R4c45ngdJCrZwiivU1yrRz.png"
                    alt="RETISTAR Logo"
                    className="h-10 md:h-10"
                  />
                </div>
                <span className="text-[0.6rem] text-black hidden md:block flex px-0">
                  REAL TIME STATISTICAL ARBITRAGE BETTING
                </span>
              </div>
            </Link>
          </div>

          <div className="hidden md:flex items-center gap-4">
            <Button
              onClick={() => router.push("/dashboard")}
              variant="secondary"
              className="bg-black text-white border border-black hover:bg-gray-900"
            >
              Dashboard
            </Button>

            {isLoggedIn && (
              <Button
                onClick={handleLogout}
                variant="secondary"
                className="bg-white text-black border border-black hover:bg-gray-100"
              >
                Logout
              </Button>
            )}
          </div>

          <div className="md:hidden">
            <button onClick={toggleMenu} className="text-black">
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="pt-4 pb-3 border-t border-gray-200 bg-white">
            <div className="flex flex-col px-5 gap-3">
              <Link
                href="/dashboard"
                className="block bg-black text-white py-2 px-4 rounded hover:bg-gray-900 transition"
              >
                Dashboard
              </Link>

              {isLoggedIn && (
                <button
                  onClick={handleLogout}
                  className="block bg-white text-black py-2 px-4 rounded border border-black hover:bg-gray-100 transition"
                >
                  Logout
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
