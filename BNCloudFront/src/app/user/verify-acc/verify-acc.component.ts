import {Component, ElementRef, Input, QueryList, ViewChildren} from '@angular/core';
import {MatSnackBar} from '@angular/material/snack-bar';
import {AuthService} from '../../services/auth-service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-verify-acc',
  standalone: false,
  templateUrl: './verify-acc.component.html',
  styleUrl: './verify-acc.component.css'
})
export class VerifyAccComponent {
code: string = ''

  username: string = ''

  constructor(private snackBar : MatSnackBar,
              private authService: AuthService,
              private router : Router
  ){
    this.username = history.state['username'] || '';

  }

  @ViewChildren('codeInput') inputs!: QueryList<ElementRef<HTMLInputElement>>;



  onVerify(event: Event): void {
    event.preventDefault();
    console.log(this.code);

    if (this.code.length < 6) {
      this.snackBar.open('Please enter all 6 digits.','Close',{duration:2000});
      return;
    }
    console.log(this.username);

    // TODO: call your backend here
    this.authService.verifyCode({'username' : this.username, 'code' : this.code}).subscribe({
      next : (res)=>{
          this.snackBar.open("Successfully activated account!")
          this.router.navigate(['/home']);
      },
      error : (err) => {
        this.snackBar.open(err)
        if(err.status === 401){}
      }
    });
  }
}
