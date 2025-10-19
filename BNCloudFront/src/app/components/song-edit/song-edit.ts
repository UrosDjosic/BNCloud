import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { SongService } from '../../services/song-service';
import { ArtistService } from '../../services/artist-service';
import { GenreService } from '../../services/genre-service';

@Component({
  selector: 'app-song-edit',
  templateUrl: './song-edit.html',
  styleUrls: ['./song-edit.css'],
  standalone: false
})
export class SongEditComponent implements OnInit {
  song: any;
  songId?: string;
  artists: any[] = [];
  availableGenres: any[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private ss: SongService,
    private as: ArtistService,
    private gs: GenreService
  ) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.songId = params.get('songId') || undefined;
      if (this.songId) this.loadSong(this.songId);
    });
    this.loadArtists();
    this.loadGenres();
  }

  loadSong(id: string) {
    this.ss.getSong(id).subscribe((res: any) => {
      this.song = { ...res, genresText: res.genres?.map((g: any) => g.name).join(', ') };
    });
  }

  loadArtists() {
    this.as.getArtists('', 50).subscribe(res => {
      this.artists = res.items;
    });
  }

  loadGenres() {
    this.gs.getAll().subscribe(res => {
      this.availableGenres = res.genres;
    });
  }

  toggleGenre(genre: any) {
    const index = this.song.genres.findIndex((g: any) => g.name === genre.name);
    if (index > -1) this.song.genres.splice(index, 1);
    else this.song.genres.push({ id: '', name: genre.name });
  }

  isGenreSelected(genre: any) {
    return this.song.genres?.some((g: any) => g.name === genre.name);
  }

  updateGenres() {
    if (this.song.genresText) {
      this.song.genres = this.song.genresText.split(',').map((g: string) => ({ id: '', name: g.trim() }));
    }
  }

  saveSong() {
    this.ss.updateSong(this.songId!, this.song).subscribe(() => {
      this.router.navigate(['/song', this.songId]);
    });
  }

  cancelEdit() {
    this.router.navigate(['/song', this.songId]);
  }

  uploadPicture() {

  }

  uploadSong() {

  }
}
