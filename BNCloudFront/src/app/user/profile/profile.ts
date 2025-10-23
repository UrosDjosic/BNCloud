import {Component, OnInit} from '@angular/core';
import {UserProfile} from '../../models/user-profile';
import {Router} from '@angular/router';
import {JwtClaims} from '../../models/jwt-claims';
import {jwtDecode} from 'jwt-decode';
import {AuthService} from '../../services/auth-service';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { ViewChild, TemplateRef } from '@angular/core';
import {UserlistService} from '../../services/userlist-service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.html',
  styleUrl: './profile.css',
  standalone: false
})
export class Profile implements OnInit {
  @ViewChild('newListDialog') newListDialog!: TemplateRef<any>;
  newListName = '';
  dialogRef?: MatDialogRef<any>;

  claims!: JwtClaims;
  user?: UserProfile;
  userLists: any = [];
  role : string = '';

  constructor(private router: Router, private authService: AuthService, private dialog: MatDialog, private us: UserlistService) {}

  ngOnInit() {
    this.role = this.authService.getRole();
    //decode jwt token
    if (!localStorage['idToken']) {
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
    if (this.user) {
      this.loadLists();
    }
  }

  goToList(listId: string) {
    this.router.navigate([`/user-list/${listId}`]);
  }

  goToSubscriptions() {
    this.router.navigate(['/subscriptions']);
  }

  loadLists() {
    this.us.getUsersUserlists(this.claims.sub).subscribe({
      next: (res: any) => {this.userLists = res.usersLists; console.log(this.userLists);},
      error: (err) => {console.log(err)}
    })
  }

  createList() {
    this.newListName = ''; // reset input
    this.dialogRef = this.dialog.open(this.newListDialog);
  }

  closeDialog() {
    this.dialogRef?.close();
  }

  confirmDialog() {
    this.dialogRef?.close(this.newListName);
    console.log('User entered list name:', this.newListName);
    this.us.createUserlist({
      name: this.newListName,
      user: this.claims.sub,
      songs: []
      }).subscribe({
      next: (res: any) => {console.log(res);},
      error: (err) => {console.log(err)}
    })
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/']).then(() => {window.location.reload();});
  }
}
