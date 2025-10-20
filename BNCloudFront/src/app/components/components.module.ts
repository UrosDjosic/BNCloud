import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';
import { MatSelectModule } from '@angular/material/select';
import { MatSliderModule } from '@angular/material/slider';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialogModule } from '@angular/material/dialog';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';

import { Album } from './album/album';
import { Artist } from './artist/artist';
import { ArtistCrud } from './artist-crud/artist-crud';
import { ContentUpload } from './content-upload/content-upload';
import { Discover } from './discover/discover';
import { Downloads } from './downloads/downloads';
import { Error } from './error/error';
import { Home } from './home/home';
import { Navbar } from './navbar/navbar';
import { Notifications } from './notifications/notifications';
import { Search } from './search/search';
import { Song } from './song/song';
import { SongEditComponent } from './song-edit/song-edit';
import { Subscriptions } from './subscriptions/subscriptions';
import { ConfirmDialogComponent } from './confirm-dialog/confirm-dialog.component';

@NgModule({
  declarations: [
    Album,
    Artist,
    ArtistCrud,
    ContentUpload,
    Discover,
    Downloads,
    Error,
    Home,
    Navbar,
    Notifications,
    Search,
    Song,
    SongEditComponent,
    Subscriptions,
    ConfirmDialogComponent
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    HttpClientModule,
    RouterModule,
    BrowserAnimationsModule,
    FormsModule,
    // Material Modules
    MatButtonModule,
    MatInputModule,
    MatCardModule,
    MatListModule,
    MatSelectModule,
    MatSliderModule,
    MatIconModule,
    MatFormFieldModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatSnackBarModule,
    MatDialogModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatProgressBarModule
  ],
  exports: [Navbar]
})
export class ComponentsModule {}
