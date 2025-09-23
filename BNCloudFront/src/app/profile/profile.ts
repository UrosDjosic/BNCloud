import {Component, OnInit} from '@angular/core';
import {UserProfile} from '../models/user-profile';
import {Router} from '@angular/router';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.html',
  styleUrl: './profile.css',
  standalone: false
})
export class Profile implements OnInit {

  user?: UserProfile;

  constructor(private router: Router) {}

  ngOnInit() {
    // Example: fetching user info
    // probably through localstorage jwtokened id or sum shit, idk
    // this.userService.getCurrentUser().subscribe(res => this.user = res);

    // Dummy data
    this.user = {
      firstName: 'Jane',
      lastName: 'Doe',
      birthDate: '1995-08-15',
      username: 'janedoe',
      email: 'jane@example.com'
    };
  }

  goToLists() {
    this.router.navigate(['/my-lists']);
  }

  goToSubscriptions() {
    this.router.navigate(['/subscriptions']);
  }
}
