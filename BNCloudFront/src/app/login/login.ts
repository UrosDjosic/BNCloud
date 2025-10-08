import {Component, OnInit,signal} from '@angular/core';
import {FormBuilder} from '@angular/forms';
import {Router} from '@angular/router';
import {MatSnackBar} from '@angular/material/snack-bar';
import {Validators} from '@angular/forms';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { AuthService } from '../auth/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.html',
  styleUrl: './login.css',
  standalone: false
})
export class Login implements OnInit {

  loginForm: any;
  isAuthenticated = signal(false); // signal<boolean>
  userData = signal<any>(null);    // signal to store user info
  userRole = signal<string>('');

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private snackBar: MatSnackBar,
    private oidcService : OidcSecurityService,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required]],
      password: ['', [Validators.required]]
    });
  }

  get f() : any { return this.loginForm.controls; }

  onSubmit() {
    if (this.loginForm.invalid) {
      this.snackBar.open('Please enter username and password', 'Close', { duration: 3000 });
      return;
    }
    this.snackBar.open("Pretend we logged in!")

  }

  goToRegister() {
    this.router.navigate(['/register']);
  }
}
