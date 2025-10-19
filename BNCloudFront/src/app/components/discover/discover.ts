import {Component, OnInit} from '@angular/core';
import {ArtistDTO} from '../../models/artist';
import {Router} from '@angular/router';
import {GenreService} from '../../services/genre-service';
import {GenreDiscoverResponse} from '../../dto/genre-discover-response';
import {DiscoverResponse} from '../../dto/discover-response';

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

  genres: GenreDiscoverResponse[] = [];
  artists: DiscoverResponse[] = [];
  albums: DiscoverResponse[] = [];

  constructor(private router: Router,
              private genreService: GenreService,) {}

  ngOnInit() {
    this.loadGenres();
  }

  loadGenres() {
    this.genreService.getAll().subscribe(res => {
      this.genres = res.genres;
    })
  }

  onGenreChange() {
    if (!this.selectedGenre) return;
    this.genreService.discover(this.selectedGenre).subscribe(res => {
      this.artists = res!.artists || [];
      this.albums = res!.albums || [];
      console.log(this.artists);
    })
  }

  navigateToArtist(songId: string) {
    this.router.navigate([`/author/${songId}`]);
  }

  navigateToAlbum(authorId: string) {
    this.router.navigate([`/album/${authorId}`]);
  }
}
