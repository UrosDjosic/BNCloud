import {Component, OnInit} from '@angular/core';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-content-rud',
  templateUrl: './content-rud.html',
  styleUrl: './content-rud.css',
  standalone: false
})
export class ContentRud implements OnInit {

  songs: any = [];
  selectedSong?: any;
  editedGenres: string = '';

  constructor(private snackBar: MatSnackBar) {}

  ngOnInit() {
    this.loadSongs();
  }

  loadSongs() {
    // this.contentService.getAllSongs().subscribe(res => this.songs = res);

  }

  selectSong(song: any) {
    this.selectedSong = { ...song }; // copy to avoid direct mutation
    this.editedGenres = song.genres.join(', ');
  }

  updateSong() {
    if (!this.selectedSong) return;

    // Parse genres
    this.selectedSong.genres = this.editedGenres.split(',').map(g => g.trim()).filter(g => g);

    // Call backend update
    // this.contentService.updateSong(this.selectedSong.id, this.selectedSong).subscribe({
    //   next: res => this.snackBar.open('Song updated successfully', 'Close', { duration: 3000 }),
    //   error: err => this.snackBar.open('Failed to update song', 'Close', { duration: 3000 })
    // });

    this.snackBar.open('Dummy: Song updated', 'Close', { duration: 3000 });
  }

  deleteSong() {
    if (!this.selectedSong) return;

    // this.contentService.deleteSong(this.selectedSong.id).subscribe({
    //   next: res => {
    //     this.snackBar.open('Song deleted', 'Close', { duration: 3000 });
    //     this.loadSongs();
    //     this.selectedSong = undefined;
    //   },
    //   error: err => this.snackBar.open('Failed to delete song', 'Close', { duration: 3000 })
    // });

    this.snackBar.open('Dummy: Song deleted', 'Close', { duration: 3000 });
    this.selectedSong = undefined;
  }
}
