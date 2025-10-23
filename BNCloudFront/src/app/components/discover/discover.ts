import {Component, OnInit} from '@angular/core';
import {ArtistDTO} from '../../models/artist';
import {ActivatedRoute, Router} from '@angular/router';
import {GenreService} from '../../services/genre-service';
import {GenreDiscoverResponse} from '../../dto/genre-discover-response';
import {DiscoverResponse} from '../../dto/discover-response';
import {TokenService} from '../../services/token-service';
import {Subscription} from 'rxjs';
import {SubscriptionService} from '../../services/subscription-service';
import {MatSnackBar} from '@angular/material/snack-bar';
import {AuthService} from '../../services/auth-service';

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

  role : string = '';

  constructor(private router: Router,
              private route: ActivatedRoute,
              private genreService: GenreService,
              private tokenService: TokenService,
              private subscriptionService: SubscriptionService,
              private snackBar: MatSnackBar,
              private authService: AuthService) {}

  ngOnInit() {
    this.role = this.authService.getRole();
    this.loadGenres();
    this.email = this.tokenService.getUserEmailFromToken();
    const genreName = this.route.snapshot.paramMap.get('name');
    if (genreName) {
      this.selectedGenre = genreName;
      this.onGenreChange();
    }
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
      user_email: this.email,
      sub_type: 'genre',
    }).subscribe({
      next: (res) => {
        this.snackBar.open(
          `Subscribed to genre ${this.currentGenre!.name}`,
          'Close',
          { duration: 3000 }
        );
      },
      error: (err) => {
        if (err.status === 409) {
          // Already subscribed
          this.snackBar.open(
            `Already subscribed to ${this.currentGenre!.name}`,
            'Close',
            { duration: 3000 }
          );
        } else {
          console.error(err);
          this.snackBar.open(
            'Failed to subscribe. Please try again later.',
            'Close',
            { duration: 3000 }
          );
        }
      }
    });
  }

}
