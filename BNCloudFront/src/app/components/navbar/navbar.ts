import { Component } from '@angular/core';
import {Router} from '@angular/router';
import {MatIcon} from '@angular/material/icon';
import {MatButton} from '@angular/material/button';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
  standalone: false
})
export class Navbar {

  constructor(private router: Router) {}

  navigate(path: string) {
    this.router.navigate([path]);
  }
}
