/**
 * Password Credentials Configuration
 *
 * This file contains hashed passwords for authentication.
 * Passwords are hashed using SHA-256.
 *
 * Default password: changeme
 * Hash: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
 *
 * To generate a new hash, use the password-hash-generator.html tool
 */

export const credentials = {
  // IP reveal password hash (SHA-256 of "changeme")
  ipRevealPasswordHash: 'REPLACE_WITH_YOUR_PASSWORD_HASH'
};

// Debug: Log the hash on import
console.log('🔐 Loaded password hash:', credentials.ipRevealPasswordHash);
