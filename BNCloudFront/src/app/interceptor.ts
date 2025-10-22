import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor, HttpResponse, HttpErrorResponse,
} from '@angular/common/http';
import {catchError, Observable, switchMap, tap, throwError} from 'rxjs';
import { AuthService } from './services/auth-service';
import {TokenService} from './services/token-service';


@Injectable()
export class Interceptor implements HttpInterceptor {
  constructor(private authService: AuthService,
              private tokenService: TokenService,) {}

  intercept(
    req: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {

    const idToken: any = localStorage.getItem('idToken');

    let clonedReq = req;
    if (idToken) {
      clonedReq = req.clone({
        headers: req.headers.set('Authorization', "Bearer " + idToken),
      });
    }

    return next.handle(clonedReq).pipe(
      // Optional: log responses
      tap(event => {
        if (event instanceof HttpResponse) {
          console.log('Response intercepted:', event);
        }
      }),
      catchError((error: HttpErrorResponse) => {

        // If 401, try refreshing the token
        if (error.status === 0) {
          const decodedToken = this.tokenService.decodeIdToken();

          if (decodedToken?.isExpired) {
            console.log('🔑 Token expired — attempting refresh...');

            return this.authService.refresh().pipe(
              switchMap((response: any) => {
                localStorage.setItem('accessToken', response.accessToken);
                localStorage.setItem('idToken', response.idToken);

                const retryReq = req.clone({
                  headers: req.headers.set('Authorization', `Bearer ${response.accessToken}`)
                });

                return next.handle(retryReq);
              }),
              catchError(refreshError => {
                console.error('❌ Refresh failed. Logging out...', refreshError);
                this.authService.logout();
                return throwError(() => refreshError);
              })
            );
          } else {
            console.warn('Token still valid — skipping refresh.');
          }
        }

        // For other errors, just pass them along
        return throwError(() => error);
      })
    );
  }
}
