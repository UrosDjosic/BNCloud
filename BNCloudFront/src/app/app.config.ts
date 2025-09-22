import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { App } from './app';
import { AppRoutingModule } from './app.routes';
import { AdminDashboard } from './admin-dashboard/admin-dashboard';
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

@NgModule({
  declarations: [
    App,
    AdminDashboard,
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
    Subscriptions
  ],
  imports: [
    AppRoutingModule,
    Navbar,
    Player,
    BrowserModule
  ],
  bootstrap: [App]
})
export class AppConfig { }
