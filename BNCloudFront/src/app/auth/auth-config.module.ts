import { NgModule } from '@angular/core';
import { AuthModule } from 'angular-auth-oidc-client';

@NgModule({
  imports: [
    AuthModule.forRoot({
      config: {
        authority: 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_UxodU7FoD',
        redirectUrl: window.location.origin,
        postLogoutRedirectUri: window.location.origin,
        clientId: '12bf1tp92r9o2qe4gi52jpvjn0',
        scope: 'openid profile email',
        responseType: 'code',
        silentRenew: true,
        useRefreshToken: true,
        logLevel: 0, // 0 = None, 1 = Error, 2 = Warn, 3 = Info, 4 = Debug
      },
    }),
  ],
  exports: [],
})
export class AuthConfigModule {}
