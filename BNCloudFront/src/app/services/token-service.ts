import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class TokenService {

  setAccessToken(accessToken: string) {
    localStorage.setItem('accessToken', accessToken);
  }

  setIdToken(idToken: string) {
    localStorage.setItem('idToken', idToken);
  }

  getAccessToken() {
    return localStorage.getItem('accessToken');
  }

  getIdToken(): string | null {
    return localStorage.getItem('idToken');
  }

  decodeIdToken() {
    const idToken = this.getIdToken();
    if (!idToken) return null;

    try {
      const base64Url = idToken.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const payload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      const decoded = JSON.parse(payload);
      const currentTime = Math.floor(Date.now() / 1000);
      decoded.isExpired = decoded.exp ? decoded.exp < currentTime : true;

      return decoded;
    } catch (e) {
      console.error('Failed to decode ID token:', e);
      return null;
    }
  }


  getUserEmailFromToken(): string | null {
    const decoded = this.decodeIdToken();
    if (!decoded) return null;
    return decoded['email'] || null;
  }
}
