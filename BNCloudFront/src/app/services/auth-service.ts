import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { LoginResponse } from '../dto/login-response';
import { LoginRequest } from '../dto/login-request';
import { RegisterRequest } from '../dto/register.request';
import { environment } from '../../env/enviroment';



@Injectable({
  providedIn: 'root'
})
export class AuthService {
 

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<LoginResponse> {
    const payload: LoginRequest = { username, password };
    return this.http.post<LoginResponse>(`${environment.apiHost}/login`, payload);
  }
   register(registerRequest: RegisterRequest): Observable<void> {
    return this.http.post<void>(`${environment.apiHost}/register`,registerRequest)
  }
}
