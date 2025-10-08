import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, ValidationErrors, ValidatorFn, Validators, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../services/auth-service';
import { createRegisterRequest, RegisterRequest } from '../dto/register.request';

@Component({
  selector: 'app-register',
  templateUrl: './register.html',
  styleUrl: './register.css',
  standalone: false
})
export class Register implements OnInit {

  registerForm!: FormGroup;
  private registerRequest : RegisterRequest = createRegisterRequest()

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private snackBar: MatSnackBar,
    private authService: AuthService
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
    if(this.registerForm.invalid){
      this.snackBar.open('Invalid form','Close',{duration : 3000})
    }
    this.registerRequest.email = this.registerForm.get('email')?.value ?? '';
    this.registerRequest.username = this.registerForm.get('username')?.value ?? '';
    this.registerRequest.password = this.registerForm.get('password')?.value ?? '';
    this.registerRequest.firstName = this.registerForm.get('firstName')?.value ?? '';
    this.registerRequest.lastName = this.registerForm.get('lastName')?.value ?? '';
    const rawDate = this.registerForm.get('birthDate')?.value;
    this.registerRequest.birthDate = rawDate  ? new Date(rawDate).toISOString().split('T')[0] : ''

    this.authService.register(this.registerRequest).subscribe({
      next: (res) => {
        this.snackBar.open('Succesfully registered!');
        this.router.navigate(['/login'])
      },
      error: (err) => console.error(err)
    });

    
  }

  goToLogin() {
    this.router.navigate(['/login']);
  }
}
