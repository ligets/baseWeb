import {NextResponse} from "next/server";
import {ParseToken} from "@/utils/auth";
import axios from "axios";


const authRoutes = ['/profile'];
const adminRoutes = ['/admin'];
const guestRoutes = ["/forgot-password", "/login", "/password-reset", "/register"];


export async function middleware(request) {
    const token = request.cookies.get('access_token')

    const isAuthRoute = authRoutes.some((route) => request.nextUrl.pathname.startsWith(route));
    const isGuestRoute = guestRoutes.some((route) => request.nextUrl.pathname.startsWith(route));
    const isAdminRoute = adminRoutes.some((route) => request.nextUrl.pathname.startsWith(route));

    if (!token && (isAuthRoute || isAdminRoute)) {
        const redirectUrl = new URL("/login", request.url);
        redirectUrl.searchParams.set("callbackUrl", request.nextUrl.href);
        return NextResponse.redirect(redirectUrl);
    }

    const response = NextResponse.next()
    const redirect = NextResponse.redirect(request.headers.get('referer') || new URL('/', request.url))

    if (token) {
        try {
            if (isGuestRoute) {
                return redirect
            }

            const decoded = ParseToken(token.value)

            const currentTime = Math.floor(Date.now() / 1000);

            if (decoded.exp <= currentTime) {
                const res = await fetch(`${process.env.BACKEND_HOST}/Authentication/Refresh`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({"refreshToken": request.cookies.get("refresh_token").value}),
                });
                const data = await res.json()
                if (res.ok) {
                    response.cookies.set(
                        'access_token',
                        "Bearer%20" + data.access_token,
                        {
                            expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
                            path: '/',
                            httpOnly: true
                        }
                    )
                    response.cookies.set(
                        'refresh_token',
                        data.refresh_token,
                        {
                            expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
                            path: '/',
                            httpOnly: true
                        }
                    )
                    const newDecoded = ParseToken(data.access_token)
                    if (isAdminRoute && newDecoded.role !== "admin") {
                        const redirect = NextResponse.redirect(
                            request.headers.get("referer") || new URL("/", request.url)
                        );
                        redirect.cookies.set("access_token", "Bearer%20" + data.access_token, {
                            expires: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
                            path: "/",
                            httpOnly: true,
                        });
                        redirect.cookies.set("refresh_token", data.refresh_token, {
                            expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
                            path: "/",
                            httpOnly: true,
                        });
                        return redirect;
                    }
                }
                else {
                    const redirect = NextResponse.redirect('/login')
                    redirect.cookies.delete('access_token')
                    redirect.cookies.delete('refresh_token')
                    return redirect
                }
            }

            if (isAdminRoute && decoded.role !== 'admin') {
                return redirect;
            }
            return response
        } catch (err) {
            redirect.cookies.delete('access_token')
            redirect.cookies.delete('refresh_token')
            return redirect
        }
    }
    return response
}

export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - api (API routes)
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         */
        '/((?!api|_next/static|_next/image|favicon.ico).*)',
    ],
}