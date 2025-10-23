import { Injectable } from '@angular/core';
import {
  CanActivate,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
  Router,
} from '@angular/router';
import {AuthService} from '../services/auth-service';



@Injectable({
  providedIn: 'root',
})
export class RoleGuard implements CanActivate {
  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    const user = this.authService.user$.getValue();

    if (!user) {
      console.log('No user, redirecting to login');
      this.router.navigate(['login']);
      return false;
    }

    const userRole = user.toUpperCase();
    console.log('User role:', userRole);

    if (!route.data['role']?.includes(userRole)) {
      console.log('User role not allowed, redirecting to home');
      this.router.navigate(['home']);
      return false;
    }

    return true;
  }
}
