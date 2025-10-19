import { NgModule } from '@angular/core';
import {CommonModule, TitleCasePipe} from '@angular/common';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import { MatButtonModule } from "@angular/material/button";
import { MatInputModule } from '@angular/material/input';
import { RouterModule } from "@angular/router";
import {HttpClientModule} from '@angular/common/http';
import { Album } from './album/album';
import { Artist } from './artist/artist';
import { ArtistCrud } from './artist-crud/artist-crud';
import { ContentRud } from './content-rud/content-rud';
import { ContentUpload } from './content-upload/content-upload';
import { Discover } from './discover/discover';
import { Downloads } from './downloads/downloads';
import { Home } from './home/home';
import { Navbar } from './navbar/navbar';
import { Notifications } from './notifications/notifications';
import { Search } from './search/search';
import { Song } from './song/song';
import {SongEditComponent} from './song-edit/song-edit';
import { Subscriptions } from './subscriptions/subscriptions';
import { Error } from './error/error';
import {MatSelect, MatSelectModule} from '@angular/material/select';
import {MatSlider} from '@angular/material/slider';
import { MatIconModule } from '@angular/material/icon';

import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';
import { MatSliderModule } from '@angular/material/slider';
import {AppRoutingModule} from '../app.routes';
import {BrowserModule} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatDatepickerModule} from '@angular/material/datepicker';
import {MatNativeDateModule, MatOption} from '@angular/material/core';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatChip, MatChipsModule} from '@angular/material/chips';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatProgressBar} from "@angular/material/progress-bar";



@NgModule({
  declarations: [
    Album,
    Artist,
    ArtistCrud,
    ContentRud,
    ContentUpload,
    Discover,
    Downloads,
    Error,
    Home,
    Navbar,
    Notifications,
    Search,
    Song,
    Subscriptions,
    SongEditComponent,
  ],
  exports: [
    Navbar
  ],
    imports: [
        CommonModule,
        ReactiveFormsModule,
        HttpClientModule,
        RouterModule,
        BrowserAnimationsModule,
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
        FormsModule,
        MatChipsModule,
        MatProgressSpinnerModule,
        MatChip,
        MatProgressSpinnerModule,
        MatProgressBar
    ]
})
export class ComponentsModule { }
