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
  userLists: UserList[] = [];

  constructor(private router: Router) {}

  ngOnInit() {
    // Example: fetching user info
    // this.userService.getCurrentUser().subscribe(res => this.user = res);

    // Dummy data
    this.user = {
      firstName: 'Jane',
      lastName: 'Doe',
      birthDate: '1995-08-15',
      username: 'janedoe',
      email: 'jane@example.com'
    };

    // Example: fetching lists
    // this.userService.getUserLists().subscribe(res => this.userLists = res);

    // Dummy lists
    this.userLists = [
      { id: '1', name: 'Favorites' },
      { id: '2', name: 'Workout Mix' },
      { id: '3', name: 'Chill Vibes' }
    ];
  }

  goToList(listId: string) {
    this.router.navigate([`/user-list/${listId}`]);
  }

  goToSubscriptions() {
    this.router.navigate(['/subscriptions']);
  }

  createList() {
    //absolutely fuckall
  }
}

interface UserList {
  id: string;
  name: string;
}
