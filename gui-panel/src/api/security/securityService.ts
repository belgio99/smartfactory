import bcrypt from 'bcrypt';

const SALT_ROUNDS = 10; // It's possibile change this value

/**
 * Methods for hashing and verifying passwords.
 * @param password - The password needed to be hashed.
 * @returns Promise will return the hashed password.
 */
export const hashPassword = async (password: string): Promise<string> => {
  try {
    const salt = await bcrypt.genSalt(SALT_ROUNDS);
    const hashedPassword = await bcrypt.hash(password, salt);
    return hashedPassword;
  } catch (error) {
    console.error('Error hashing password:', error);
    throw new Error('Failed to hash password');
  }
};

/**
 * Method used to verify password with hashed password.
 * @param password - Password needs to verify.
 * @param hashedPassword - HashPassword will be check with password.
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