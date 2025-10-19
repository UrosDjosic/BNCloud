import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { LoginResponse } from '../dto/login-response';
import { LoginRequest } from '../dto/login-request';
import { RegisterRequest } from '../dto/register.request';
import { environment } from '../../env/enviroment';
import { VerificationRequest } from '../dto/verification-request';
import {JwtHelperService} from '@auth0/angular-jwt';
import {RefreshResponse} from '../dto/refresh-response';
import {TokenService} from './token-service';



@Injectable({
  providedIn: 'root'
})
export class AuthService {

  user$ = new BehaviorSubject<string>('');
  userState = this.user$.asObservable();

  constructor(private http: HttpClient, private tokenService: TokenService) {
    // Initialize user from localStorage on service creation
    const storedRole = this.getRole();
    this.user$.next(storedRole ? storedRole.toUpperCase() : '');
  }
  login(username: string, password: string): Observable<LoginResponse> {
    const payload: LoginRequest = { username, password };
    return this.http.post<LoginResponse>(`${environment.apiHost}/login`, payload);
  }
   register(registerRequest: RegisterRequest): Observable<void> {
    return this.http.post<void>(`${environment.apiHost}/register`,registerRequest)
  }
  verifyCode(verifyRequest : VerificationRequest) : Observable<void> {
    return this.http.put<void>(`${environment.apiHost}/verify`,verifyRequest)
  }
  refresh(): Observable<RefreshResponse> {
    return this.http.put<RefreshResponse>(
      environment.apiHost + '/login/refresh',
      {},
      { withCredentials: true }
    );
  }
  logout() {
    localStorage.clear();
  }

  getRole(): string {
    if (this.isLoggedIn()) {
      const idToken = this.tokenService.getIdToken();
      if (!idToken) return '';

      const helper = new JwtHelperService();
      const decoded = helper.decodeToken(idToken);

      const groups = decoded?.['cognito:groups'];
      if (!groups || !Array.isArray(groups) || groups.length === 0) {
        console.warn('No groups found in decoded token', decoded);
        return '';
      }

      return groups[0];
    }
    return '';
  }


  isLoggedIn(): boolean {
    return localStorage.getItem('accessToken') != null && localStorage.getItem('idToken') != null;
  }

  setUser(): void {
    this.user$.next(this.getRole().toUpperCase());
  }

}
