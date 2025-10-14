import {Injectable} from '@angular/core';


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
  getIdToken() : string | null {
    return localStorage.getItem('idToken');
  }

  decodeIdToken() {
    const idToken = this.getIdToken() ? this.getIdToken() : ''
    if (!idToken) return null;
    const payload = atob(idToken.split('.')[1]);
    return JSON.parse(payload)
  }

}
