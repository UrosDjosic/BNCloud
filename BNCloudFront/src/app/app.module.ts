import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { App } from './app';
import { AppRoutingModule } from './app.routes';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import {MatDivider, MatList} from '@angular/material/list';
import {MatListItem} from '@angular/material/list';
import {MatOption} from '@angular/material/core';
import {MatSelect} from '@angular/material/select';
import { HttpClientModule } from '@angular/common/http';
import { ComponentsModule } from './components/components.module';
import {UserModule} from './user/user.module';


@NgModule({
  declarations: [
    App
  ],
  imports: [
    ComponentsModule,
    UserModule,
    AppRoutingModule,
    HttpClientModule,
    BrowserModule,
    BrowserAnimationsModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatButtonModule,
    MatSnackBarModule,
    MatList,
    MatListItem,
    MatOption,
    MatSelect,
    MatDivider,
    FormsModule
  ],
  bootstrap: [App]
})
export class AppConfig { }
