import { Component } from '@angular/core';
import {NavigationEnd, Route, Router} from '@angular/router';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { AuthService } from './services/auth-service';
import {filter} from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrls: ['./app.css'],
  standalone: false
})
export class App {
  title = 'BNCloudFront';
  showSidebar: boolean = false;

  constructor(
    private router: Router,
    private authService: AuthService,
  ) {}

  ngOnInit(){
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: any) => {
        this.setSidebarState(event.urlAfterRedirects);
      });

  }
  setSidebarState(url: string) {
    const hideSidebarPaths = ['/login', '/register'];
    this.showSidebar = !hideSidebarPaths.some(path => url.startsWith(path));
  }

  isInvalidRoute(url: string): boolean {
    const validRoutes = this.getValidRoutes();
    return !validRoutes.some(route => url.startsWith(route));
  }

  getValidRoutes(): string[] {
    const routes: string[] = [];

    this.router.config.forEach((route: Route) => {
      if (route.path) {
        const basePath = route.path.split('/')[0];
        routes.push(`/${basePath}`);
      }
    });

    return routes;
  }
}
