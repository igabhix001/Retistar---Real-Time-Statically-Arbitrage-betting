import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  const token = request.cookies.get("token")?.value || null;

  if (request.nextUrl.pathname.startsWith("/dashboard") && !token) {
    // Redirect to login if no token
    return NextResponse.redirect(new URL("/login", request.url));
  }

  try {
    // Call the backend to validate the session
    const response = await fetch("http://localhost:8000/auth/check-session", {
      headers: { cookie: request.headers.get("cookie") || "" },
    });

    if (!response.ok) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
  } catch (error) {
    console.error("Middleware session validation error:", error);
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}
