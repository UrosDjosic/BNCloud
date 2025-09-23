import {Component, OnInit} from '@angular/core';
import {FormBuilder} from '@angular/forms';
import {Router} from '@angular/router';
import {MatSnackBar} from '@angular/material/snack-bar';
import {Validators} from '@angular/forms';

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
    const formValue = this.loginForm.value;
    this.snackBar.open('Pretend we logged in 🎉', 'Close', { duration: 3000 });
  }

  goToRegister() {
    this.router.navigate(['/register']);
  }
}
