import { Component } from '@angular/core';
import {Router} from '@angular/router';
import {MatIcon} from '@angular/material/icon';
import {MatButton} from '@angular/material/button';
import {AuthService} from '../../services/auth-service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
  standalone: false
})
export class Navbar {
  isLoggedIn: boolean = false;
  role : string = '';
  constructor(private router: Router,private authService: AuthService) {}

  ngOnInit() {
    this.authService.userState.subscribe(user => {
      this.isLoggedIn = !(user === '' || user == null);
      if (!(user === '' || user == null)){
        this.role = user.toUpperCase();
      }
    })
  }

  navigate(path: string) {
    this.router.navigate([path]);

  }
}
