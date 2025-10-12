import { NgModule } from '@angular/core';
// Angular Material Modules
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatListModule } from '@angular/material/list';
import { MatDialogModule } from '@angular/material/dialog';
import {Register} from './register/register';
import {Login} from './login/login';
import {Profile} from './profile/profile';
import {UserList} from './user-list/user-list';
import {VerifyAccComponent} from './verify-acc/verify-acc.component';
import {RouterModule} from '@angular/router';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {MatSliderModule} from '@angular/material/slider';
import {MatSelectModule} from '@angular/material/select';
import {MatSnackBarModule} from '@angular/material/snack-bar';

@NgModule({
  declarations: [Register, Login, Profile, UserList,VerifyAccComponent],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    ReactiveFormsModule,
    RouterModule,
    MatCardModule,
    MatListModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSliderModule,
    MatSelectModule,
    MatSnackBarModule,
    MatDatepickerModule,
    FormsModule,
  ]
})
export class UserModule {}
