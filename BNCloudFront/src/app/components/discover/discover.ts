import {Component, OnInit} from '@angular/core';
import {ArtistDTO} from '../../models/artist';
import {Router} from '@angular/router';
import {GenreService} from '../../services/genre-service';
import {GenreDiscoverResponse} from '../../dto/genre-discover-response';
import {DiscoverResponse} from '../../dto/discover-response';
import {TokenService} from '../../services/token-service';
import {Subscription} from 'rxjs';
import {SubscriptionService} from '../../services/subscription-service';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-discover',
  templateUrl: './discover.html',
  styleUrl: './discover.css',
  standalone: false
})
export class Discover implements OnInit {

  selectedGenre?: string;
  currentGenre?: GenreDiscoverResponse;
  songs: any = [];
  authors: ArtistDTO[] = [];
  email : string | null = null;

  genres: GenreDiscoverResponse[] = [];
  artists: DiscoverResponse[] = [];
  albums: DiscoverResponse[] = [];

  constructor(private router: Router,
              private genreService: GenreService,
              private tokenService: TokenService,
              private subscriptionService: SubscriptionService,
              private snackBar: MatSnackBar,) {}

  ngOnInit() {
    this.loadGenres();
    this.email = this.tokenService.getUserEmailFromToken();
  }

  loadGenres() {
    this.genreService.getAll().subscribe(res => {
      this.genres = res.genres;
    })
  }

  onGenreChange() {
    if (!this.selectedGenre) return;
    this.genreService.discover(this.selectedGenre).subscribe(res => {
      this.currentGenre = res;
      this.artists = res!.artists || [];
      this.albums = res!.albums || [];
      console.log(this.artists);
    })
  }

  navigateToArtist(songId: string) {
    this.router.navigate([`/artist/${songId}`]);
  }

  navigateToAlbum(authorId: string) {
    this.router.navigate([`/album/${authorId}`]);
  }

  subscribeToGenre() {
    if (!this.currentGenre || !this.email) {
      return;
    }
    this.subscriptionService.subscribe({
      subject_id: this.currentGenre.id,
      subject_name: this.currentGenre.name,
      user_email : this.email,
      sub_type: 'genre',
    }).subscribe(res => {
      this.snackBar.open(`Subscribed to genre ${this.currentGenre!.name}`, 'Close', { duration: 3000 });
    })
  }
}
