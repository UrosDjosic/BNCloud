import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { App } from './app';
import { AppRoutingModule } from './app.routes';
import { Album } from './album/album';
import { ArtistCrud } from './artist-crud/artist-crud';
import { Artist } from './artist/artist';
import { ContentRud } from './content-rud/content-rud';
import { ContentUpload } from './content-upload/content-upload';
import { Discover } from './discover/discover';
import { Downloads } from './downloads/downloads';
import { Error } from './error/error';
import { Home } from './home/home';
import { Login } from './login/login';
import { Notifications } from './notifications/notifications';
import { Profile } from './profile/profile';
import { Register } from './register/register';
import { Search } from './search/search';
import { Song } from './song/song';
import { Subscriptions } from './subscriptions/subscriptions';
import {Navbar} from './navbar/navbar';
import {Player} from './player/player';
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
import {UserList} from './user-list/user-list';
import {MatOption} from '@angular/material/core';
import {MatSelect} from '@angular/material/select';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  declarations: [
    App,
    Album,
    ArtistCrud,
    Artist,
    ContentRud,
    ContentUpload,
    Discover,
    Downloads,
    Error,
    Home,
    Login,
    Notifications,
    Profile,
    Register,
    Search,
    Song,
    Subscriptions,
    UserList
  ],
  imports: [
    AppRoutingModule,
    HttpClientModule,
    Navbar,
    Player,
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
