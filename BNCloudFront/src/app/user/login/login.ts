import {Component, OnInit,signal} from '@angular/core';
import {FormBuilder} from '@angular/forms';
import {Router} from '@angular/router';
import {MatSnackBar} from '@angular/material/snack-bar';
import {Validators} from '@angular/forms';
import { LoginResponse } from '../../dto/login-response';
import {AuthService} from '../../services/auth-service';
import {TokenService} from '../../services/token-service';

@Component({
  selector: 'app-login',
  templateUrl: './login.html',
  styleUrl: './login.css',
  standalone: false
})
export class Login implements OnInit {

  loginForm: any;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private snackBar: MatSnackBar,
    private authService: AuthService,
    private tokenService: TokenService
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
        this.snackBar.open('Succesfull login','Close',{duration : 3000})
        this.router.navigate(['/']);
        console.log(res);
        this.tokenService.setAccessToken(res.tokens.AccessToken);
        this.tokenService.setIdToken(res.tokens.IdToken);
        this.authService.setUser();
      },
      error: (err) => {
        if(err.status == 403){
           this.router.navigate(['/verify'], {
              state: { username: this.loginForm.get('username')?.value }
            });
            return;
        }else if(err.status == 401) {
          this.snackBar.open('Invalid password or username!','Close',{duration : 3000})
        }
        console.error(err);
      }
    });

  }

  goToRegister() {
    this.router.navigate(['/register']);
  }
}
