export interface User {
    id: number;
    name: string;
    email: string;
}
  
export interface LoginRequest {
    username: string;
    password: string;
}
  
export interface LoginResponse {
    token: string;
    user: User;
}