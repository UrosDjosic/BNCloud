import {Component, OnInit,signal} from '@angular/core';
import {FormBuilder} from '@angular/forms';
import {Router} from '@angular/router';
import {MatSnackBar} from '@angular/material/snack-bar';
import {Validators} from '@angular/forms';
import { LoginResponse } from '../dto/login-response';
import {AuthService} from '../services/auth-service';

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

    this.authService.login(
      this.loginForm.get('username')?.value,  // <-- use .value
      this.loginForm.get('password')?.value).subscribe({
      next: (res : LoginResponse) => {
        this.snackBar.open('Succesfull login')
        localStorage.setItem('idToken', res.tokens.IdToken);
        localStorage.setItem('accessToken', res.tokens.AccessToken);
      },
      error: (err) => {
        console.error(err);
      }
    });

  }

  goToRegister() {
    this.router.navigate(['/register']);
  }
}
