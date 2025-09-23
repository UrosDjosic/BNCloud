import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, ValidationErrors, ValidatorFn, Validators, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-register',
  templateUrl: './register.html',
  styleUrl: './register.css',
  standalone: false
})
export class Register implements OnInit {

  registerForm!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit() {
    this.registerForm = this.fb.group({
      firstName: ['', [Validators.required]],
      lastName: ['', [Validators.required]],
      birthDate: ['', [Validators.required]],
      username: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]]
    }, { validators: [this.passwordsMatchValidator()] });
  }

  get f() : any { return this.registerForm.controls; }

  passwordsMatchValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const password = control.get('password')?.value;
      const confirmPassword = control.get('confirmPassword')?.value;
      return password && confirmPassword && password !== confirmPassword
        ? { passwordMismatch: true }
        : null;
    };
  }

  onSubmit() {
    this.snackBar.open('Pretend we registered the user 🎉', 'Close', { duration: 3000 });
  }

  goToLogin() {
    this.router.navigate(['/login']);
  }
}
