import { NextResponse } from 'next/server';

export async function POST() {
  return NextResponse.json(
    {
      success: false,
      error: { message: 'MFA verification is managed by Clerk and is disabled on the current free-plan setup.' },
    },
    { status: 410 }
  );
}
