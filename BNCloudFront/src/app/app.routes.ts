import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Home } from './home/home';
import { Register } from './register/register';
import { Login } from './login/login';
import { Subscriptions } from './subscriptions/subscriptions';
import { Song } from './song/song';
import { Search } from './search/search';
import { Profile } from './profile/profile';
import { Notifications } from './notifications/notifications';
import { Error } from './error/error';
import { Downloads } from './downloads/downloads';
import { Discover } from './discover/discover';
import { ContentUpload } from './content-upload/content-upload';
import { ContentRud } from './content-rud/content-rud';
import { ArtistCrud } from './artist-crud/artist-crud';
import { Artist } from './artist/artist';
import { Album } from './album/album';
import { AdminDashboard } from './admin-dashboard/admin-dashboard';

const routes: Routes = [
  { path: '', component: Home },
  { path: 'register', component: Register },
  { path: 'login', component: Login },
  { path: 'subscriptions', component: Subscriptions },
  { path: 'song/:songId', component: Song },
  { path: 'search', component: Search },
  { path: 'profile', component: Profile },
  { path: 'notifications', component: Notifications },
  { path: 'downloads', component: Downloads },
  { path: 'discover', component: Discover },
  { path: 'content-upload', component: ContentUpload },
  { path: 'content-rud', component: ContentRud },
  { path: 'artist-crud', component: ArtistCrud },
  { path: 'artist/:artistId', component: Artist },
  { path: 'album/:albumId', component: Album },
  { path: 'dashboard', component: AdminDashboard },
  { path: '**', component: Error }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
