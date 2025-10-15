export interface JwtClaims {
  sub: string;
  email_verified: boolean;
  birthdate: string;
  "custom:lastName": string;
  "custom:firstName": string;
  iss: string;
  "cognito:username": string;
  origin_jti: string;
  aud: string;
  event_id: string;
  token_use: string;
  auth_time: number;
  exp: number;
  iat: number;
  jti: string;
  email: string;
}
