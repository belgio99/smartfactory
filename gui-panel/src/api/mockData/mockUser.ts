import bcrypt from 'bcrypt';

interface MockUser {
  userId: string;
  username: string;
  email: string;
  password: string; // Encrypted password
  role: string;
  site: string;
}

// Used to simulate the hashing (simulazione)
const hashPassword = (password: string): string => {
  const salt = bcrypt.genSaltSync(10);
  return bcrypt.hashSync(password, salt);
};

// Mock users array
export const mockUsers: MockUser[] = [
  {
    userId: '1',
    username: 'Ale',
    email: 'john.doe@example.com',
    password: hashPassword('password123'),
    role: 'Admin',
    site: 'site_a',
  },
  {
    userId: '2',
    username: 'Davide',
    email: 'jane.smith@example.com',
    password: hashPassword('securepassword'),
    role: 'FloorFactoryManager',
    site: 'site_b',
  },
  {
    userId: '3',
    username: 'alice_wonder',
    email: 'alice.wonder@example.com',
    password: hashPassword('password2024'),
    role: 'editor',
    site: 'site_c',
  },
  {
    userId: '4',
    username: 'bob_builder',
    email: 'bob.builder@example.com',
    password: hashPassword('builder42'),
    role: 'viewer',
    site: 'site_a',
  },
];

export const findUserByUsernameOrEmail = (identifier: string): MockUser | null => {
  return (
    mockUsers.find(user => user.username === identifier || user.email === identifier) || null
  );
};

export const validatePassword = (inputPassword: string, hashedPassword: string): boolean => {
  return bcrypt.compareSync(inputPassword, hashedPassword);
};