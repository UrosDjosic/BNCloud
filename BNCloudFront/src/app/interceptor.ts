import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor, HttpResponse, HttpErrorResponse,
} from '@angular/common/http';
import {catchError, Observable, switchMap, tap, throwError} from 'rxjs';
import { AuthService } from './services/auth-service';


@Injectable()
export class Interceptor implements HttpInterceptor {
  constructor(private authService: AuthService) {}

  intercept(
    req: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {

    const accessToken: any = localStorage.getItem('accessToken');

    let clonedReq = req;
    if (accessToken) {
      console.log(accessToken);
      clonedReq = req.clone({
        headers: req.headers.set('Authorization', "Bearer " + accessToken)
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
        if (error.status === 401) {
          return this.authService.refresh().pipe(
            switchMap((response: any) => {
              console.log(response);

              localStorage.setItem('accessToken', response.accessToken);
              localStorage.setItem('idToken', response.idToken);

              const retryReq = req.clone({
                headers: req.headers.set('Authorization', `Bearer ${response.accessToken}`)
              });

              return next.handle(retryReq);
            }),
            catchError(refreshError => {
              this.authService.logout();
              return throwError(() => refreshError);
            })
          );
        }

        // For other errors, just pass them along
        return throwError(() => error);
      })
    );
  }
}
