import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpResponse,
  HttpErrorResponse
} from '@angular/common/http';
import { catchError, Observable, switchMap, tap, throwError } from 'rxjs';
import { AuthService } from './services/auth-service';
import { TokenService } from './services/token-service';

@Injectable()
export class Interceptor implements HttpInterceptor {
  constructor(private authService: AuthService, private tokenService: TokenService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const isRefreshRequest = req.url.includes('/api/login/refresh');

    // Skip adding token for refresh request
    let clonedReq = req;
    if (!isRefreshRequest) {
      const idToken = localStorage.getItem('idToken');
      if (idToken) {
        clonedReq = req.clone({
          headers: req.headers.set('Authorization', 'Bearer ' + idToken),
        });
      }
    }

    return next.handle(clonedReq).pipe(
      tap(event => {
        if (event instanceof HttpResponse) {
          console.log('Response intercepted:', event);
        }
      }),
      catchError((error: HttpErrorResponse) => {

        if (
          !isRefreshRequest &&
          (error.status === 0 ||
            (error.status === 401 && error.error?.message === 'The incoming token has expired'))
        ) {
          const decodedToken = this.tokenService.decodeIdToken();

          if (decodedToken?.isExpired) {
            console.log('🔑 Token expired — attempting refresh...');

            return this.authService.refresh(localStorage.getItem('refreshToken')).pipe(
              switchMap((response: any) => {
                console.log('✅ Token refresh successful:', response);
                localStorage.setItem('accessToken', response.accessToken);
                localStorage.setItem('idToken', response.idToken);

                const retryReq = req.clone({
                  headers: req.headers.set('Authorization', `Bearer ${response.accessToken}`)
                });

                return next.handle(retryReq);
              }),
              catchError(refreshError => {
                console.error('❌ Refresh failed. Logging out...', refreshError);
                // this.authService.logout();
                return throwError(() => refreshError);
              })
            );
          } else {
            console.warn('Token still valid — skipping refresh.');
          }
        }

        return throwError(() => error);
      })
    );
  }
}
