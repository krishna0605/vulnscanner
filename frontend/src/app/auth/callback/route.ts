import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { origin, searchParams } = new URL(request.url);
  const next = searchParams.get('next') ?? '/dashboard';

  return NextResponse.redirect(`${origin}${next}`);
}
