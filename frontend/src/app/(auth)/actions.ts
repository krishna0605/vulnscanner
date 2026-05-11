'use server';

import { redirect } from 'next/navigation';

export async function login() {
  redirect('/sign-in');
}

export async function signup() {
  redirect('/sign-up');
}

export async function signInWithGoogle() {
  redirect('/sign-in');
}
