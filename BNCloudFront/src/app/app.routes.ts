import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Register } from './user/register/register';
import { Login } from './user/login/login';
import { Song } from './components/song/song';
import { Search } from './components/search/search';
import { Profile } from './user/profile/profile';
import { Notifications } from './components/notifications/notifications';
import { Error } from './components/error/error';
import { Downloads } from './components/downloads/downloads';
import { Discover } from './components/discover/discover';
import { ContentUpload } from './components/content-upload/content-upload';
import { ArtistCrud } from './components/artist-crud/artist-crud';
import { Artist } from './components/artist/artist';
import { Album } from './components/album/album';
import {UserList} from './user/user-list/user-list';
import { VerifyAccComponent } from './user/verify-acc/verify-acc.component';
import { Subscriptions } from './components/subscriptions/subscriptions';
import {SongEditComponent} from './components/song-edit/song-edit';


const routes: Routes = [
  { path: '', component: Home },
  { path: 'register', component: Register },
  { path: 'login', component: Login },
  { path: 'subscriptions', component: Subscriptions },
  { path: 'song/:songId', component: Song },
  { path: 'song/:songId/edit', component: SongEditComponent },
  { path: 'search', component: Search },
  { path: 'profile', component: Profile },
  { path: 'notifications', component: Notifications },
  { path: 'downloads', component: Downloads },
  { path: 'discover', component: Discover },
  { path: 'content-upload', component: ContentUpload },
  { path: 'artist-crud', component: ArtistCrud },
  { path: 'artist/:artistId', component: Artist },
  { path: 'album/:albumId', component: Album },
  { path: 'user-list/:userListId', component: UserList },
  { path: 'verify',component: VerifyAccComponent},
  { path: '**', component: Error }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
