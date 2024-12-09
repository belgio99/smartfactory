import bcrypt from 'bcryptjs';

/**
 * Methods for hashing and verifying passwords.
 * @param password string - The password needed to be hashed.
 * @returns Promise will return the hashed password.
 */
export const hashPassword = async (password: string): Promise<string> => {
  try {
    const saltString = 'a'.repeat(16) + 'e'.repeat(6);
    const customSalt = `$2b$12$${saltString}`;
    // Hash the password
    const hashedPassword = await bcrypt.hash(password, customSalt);
    return hashedPassword;
  } catch (error) {
    console.error('Error hashing password:', error);
    throw new Error('Failed to hash password');
  }
};

/**
 * Method used to verify password with hashed password.
 * @param password string - Password needs to verify.
 * @param hashedPassword string - HashPassword will be check with password.
 * @returns Promise returns true if password is correct, false otherwise.
 */
export const verifyPassword = async (
  password: string,
  hashedPassword: string
): Promise<boolean> => {
  try {
    return await bcrypt.compare(password, hashedPassword);
  } catch (error) {
    console.error('Error verifying password:', error);
    throw new Error('Failed to verify password');
  }
};