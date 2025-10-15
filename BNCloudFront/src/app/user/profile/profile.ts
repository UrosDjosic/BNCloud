import {Component, OnInit} from '@angular/core';
import {UserProfile} from '../../models/user-profile';
import {Router} from '@angular/router';
import {JwtClaims} from '../../models/jwt-claims';
import {jwtDecode} from 'jwt-decode';
import {AuthService} from '../../services/auth-service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.html',
  styleUrl: './profile.css',
  standalone: false
})
export class Profile implements OnInit {
  claims!: JwtClaims;
  user?: UserProfile;
  userLists: UserList[] = [];

  constructor(private router: Router, private authService: AuthService) {}

  ngOnInit() {
    //decode jwt token
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
    }
    this.claims = jwtDecode<JwtClaims>(localStorage['idToken']);
    this.user = {
      firstName: this.claims["custom:firstName"],
      lastName: this.claims["custom:lastName"],
      birthDate: this.claims["birthdate"],
      username: this.claims["cognito:username"],
      email: this.claims["email"],
    }
  }

  goToList(listId: string) {
    this.router.navigate([`/user-list/${listId}`]);
  }

  goToSubscriptions() {
    this.router.navigate(['/subscriptions']);
  }

  createList() {
    // TODO: implement later
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/']).then(() => {window.location.reload();});
  }
}

interface UserList {
  id: string;
  name: string;
}
