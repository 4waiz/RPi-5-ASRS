/**
 * Password Hashing Utility
 *
 * Provides functions to hash passwords using SHA-256
 * for secure password verification
 */

/**
 * Hash a password using SHA-256
 * @param password - The plain text password to hash
 * @returns A promise that resolves to the hashed password as a hex string
 */
export async function hashPassword(password: string): Promise<string> {
  // Encode the password as UTF-8
  const encoder = new TextEncoder();
  const data = encoder.encode(password);

  // Hash the password using SHA-256
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);

  // Convert the hash to a hex string
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(byte => byte.toString(16).padStart(2, '0')).join('');

  return hashHex;
}

/**
 * Verify a password against a stored hash
 * @param password - The plain text password to verify
 * @param storedHash - The stored hash to compare against
 * @returns A promise that resolves to true if the password matches, false otherwise
 */
export async function verifyPassword(password: string, storedHash: string): Promise<boolean> {
  const inputHash = await hashPassword(password);
  console.log('🔐 Password Hash Verification:');
  console.log('  Input password:', password);
  console.log('  Generated hash:', inputHash);
  console.log('  Stored hash:   ', storedHash);
  console.log('  Match:', inputHash === storedHash);
  return inputHash === storedHash;
}
