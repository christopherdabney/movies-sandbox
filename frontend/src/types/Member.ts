export interface RegistrationRecord {
  id?: number;
  email: string;
  verified: bool;
  password: string;
  firstName: string;
  lastName: string;
  createdAt?: string;
}