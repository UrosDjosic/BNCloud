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



@Injectable({
  providedIn: 'root'
})
export class AuthService {

  user$ = new BehaviorSubject("");
  userState = this.user$.asObservable();

  userID$ = new BehaviorSubject("");


  constructor(private http: HttpClient) {}

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

  getRole(): any {
    if (this.isLoggedIn()) {
      const accessToken: any = localStorage.getItem('user');
      const helper = new JwtHelperService();
      return helper.decodeToken(accessToken).role;
    }
    return null;
  }

  isLoggedIn(): boolean {
    return localStorage.getItem('user') != null;
  }

  setUser(): void {
    this.user$.next(this.getRole());
  }

}
