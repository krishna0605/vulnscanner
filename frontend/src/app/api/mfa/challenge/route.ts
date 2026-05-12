import { NextResponse } from 'next/server';

export async function POST() {
  return NextResponse.json(
    {
      success: false,
      error: { message: 'MFA challenges are managed by Clerk and are disabled on the current free-plan setup.' },
    },
    { status: 410 }
  );
}
