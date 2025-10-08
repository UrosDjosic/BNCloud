import { Injectable } from '@angular/core';
import { CognitoUserPool, CognitoUser, AuthenticationDetails } from 'amazon-cognito-identity-js';

const poolData = {
  UserPoolId: 'us-east-1_UxodU7FoD',
  ClientId: '12bf1tp92r9o2qe4gi52jpvjn0'
};

const userPool = new CognitoUserPool(poolData);

@Injectable({ providedIn: 'root' })
export class AuthService {
  
  private readonly TOKEN_KEY = 'access_token';

  clearToken() : string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }
  storeToken(idToken: string) {
    localStorage.setItem(this.TOKEN_KEY, idToken);
  }
  login(username: string, password: string): Promise<any> {
    const authDetails = new AuthenticationDetails({ Username: username, Password: password });
    const user = new CognitoUser({ Username: username, Pool: userPool });

    return new Promise((resolve, reject) => {
      user.authenticateUser(authDetails, {
        onSuccess: result => resolve(result),
        onFailure: err => reject(err)
      });
    });
  }
}
