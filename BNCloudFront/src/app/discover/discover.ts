import {Component, OnInit} from '@angular/core';
import {SongDTO} from '../models/song';
import {ArtistDTO} from '../models/artist';
import {Router} from '@angular/router';
import {AlbumDTO} from '../models/album';

@Component({
  selector: 'app-discover',
  templateUrl: './discover.html',
  styleUrl: './discover.css',
  standalone: false
})
export class Discover implements OnInit {

  genres: string[] = [];
  selectedGenre?: string;

  songs: SongDTO[] = [];
  authors: ArtistDTO[] = [];

  constructor(private router: Router) {}

  ngOnInit() {
    this.loadGenres();
  }

  loadGenres() {
    // this.discoverService.getGenres().subscribe(res => this.genres = res);

    // Dummy genres
    this.genres = ['Rock', 'Indie', 'Electronic', 'Jazz', 'Hip-Hop'];
  }

  onGenreChange() {
    if (!this.selectedGenre) return;

    // this.discoverService.getByGenre(this.selectedGenre).subscribe(res => {
    //   this.songs = res.songs;
    //   this.authors = res.authors;
    // });

    // Dummy filtered data
    this.songs = [
      { id: 's1', fileName: 'Fading Lights', genres: ['Rock', 'Indie'], fileType: '', size: '', createdAt: '', updatedAt: '', authors: [],
        albums: [], ratings: [] },
      { id: 's2', fileName: 'Dreamscapes', genres: ['Rock', 'Electronic'], fileType: '', size: '', createdAt: '', updatedAt: '', authors: [],
        albums: [], ratings: [] }
    ].filter(song => song.genres.includes(this.selectedGenre!));

    this.authors = [
      { id: 'a1', name: 'The Midnight Beats', genres: ['Rock', 'Electronic'], biography: ""},
      { id: 'a2', name: 'Luna Waves', genres: ['Indie', 'Rock'],biography: "" }
    ].filter(author => author.genres.includes(this.selectedGenre!));
  }

  navigateToSong(songId: string) {
    this.router.navigate([`/song/${songId}`]);
  }

  navigateToAuthor(authorId: string) {
    this.router.navigate([`/author/${authorId}`]);
  }
}
