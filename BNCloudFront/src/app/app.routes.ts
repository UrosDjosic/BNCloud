import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

// Components
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
import { UserList } from './user/user-list/user-list';
import { VerifyAccComponent } from './user/verify-acc/verify-acc.component';
import { Subscriptions } from './components/subscriptions/subscriptions';
import { SongEditComponent } from './components/song-edit/song-edit';
import { AdvancedEdit } from './components/advanced-edit/advanced-edit';
import {AuthGuard} from './auth/auth.guard';
import {RoleGuard} from './auth/role.guard';

// Guards


const routes: Routes = [
  // Public routes
  { path: '', component: Home, canActivate: [AuthGuard] },
  { path: 'register', component: Register },
  { path: 'login', component: Login },
  { path: 'verify', component: VerifyAccComponent },

  // Protected routes (AuthGuard)
  { path: 'profile', component: Profile, canActivate: [AuthGuard] },
  { path: 'downloads', component: Downloads, canActivate: [AuthGuard]},

  // Song routes
  { path: 'song/:songId', component: Song, canActivate: [AuthGuard] },
  // Discover & search (accessible but protected)
  { path: 'search', component: Search, canActivate: [AuthGuard] },
  { path: 'discover', component: Discover, canActivate: [AuthGuard] },
  { path: 'discover/:name', component: Discover, canActivate: [AuthGuard] },

  // Role-protected routes (Admin or Creator)
  {
    path: 'content-upload',
    component: ContentUpload,
    canActivate: [RoleGuard],
    data: { role: ['ADMINISTRATOR'] }
  },
  {
    path: 'artist-crud',
    component: ArtistCrud,
    canActivate: [RoleGuard],
    data: { role: ['ADMINISTRATOR'] }
  },
  { path: 'subscriptions',
    component: Subscriptions,
    canActivate: [RoleGuard],
    data: {role:['USER']}
  },
  { path: 'song/:songId/edit',
    component: SongEditComponent,
    canActivate: [RoleGuard],
    data: {role:['ADMINISTRATOR']}
  },
  { path: 'advanced-edit/:songId/:audioUrl/:imageUrl',
    component: AdvancedEdit,
    canActivate: [RoleGuard],
    data: {role:['ADMINISTRATOR']}
  },


  // Artist & album (any logged-in user)
  { path: 'artist/:artistId', component: Artist, canActivate: [AuthGuard] },
  { path: 'album/:albumId', component: Album, canActivate: [AuthGuard] },
  { path: 'user-list/:userListId', component: UserList, canActivate: [AuthGuard] },

  // Fallback
  { path: '**', component: Error },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
