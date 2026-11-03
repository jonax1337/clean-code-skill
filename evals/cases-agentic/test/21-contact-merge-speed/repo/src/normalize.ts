/** The form of an email address that is compared when looking for duplicate contacts. */
export function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}
