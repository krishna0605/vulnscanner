import { NextResponse } from 'next/server';

const disabled = {
  success: false,
  enabled: false,
  error: { message: 'MFA is managed by Clerk and is disabled on the current free-plan setup.' },
};

export async function GET() {
  return NextResponse.json(disabled, { status: 200 });
}

export async function POST() {
  return NextResponse.json(disabled, { status: 410 });
}
