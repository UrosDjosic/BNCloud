import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {MatSnackBar} from '@angular/material/snack-bar';
import {ArtistService} from '../../services/artist-service';

@Component({
  selector: 'app-artist',
  templateUrl: './artist.html',
  styleUrl: './artist.css',
  standalone: false
})
export class Artist implements OnInit {

  artistId?: string;
  artist?: any;

  constructor(private route: ActivatedRoute, private snackBar: MatSnackBar, private as: ArtistService) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.artistId = params.get('artistId') || undefined;
      if (this.artistId) {
        this.loadArtist(this.artistId);
      }
    });
  }

  loadArtist(artistId: string) {
    this.as.getArtist(artistId).subscribe({
      next: (artist: any) => {
        console.log(artist.Songs);
        this.artist = artist; // ✅ assign response to artist
      },
      error: (err) => {
        console.error(err);
        this.snackBar.open('Failed to load artist 😞', 'Close', { duration: 3000 });
      }
    });
  }

  subscribeArtist() {
    // this.userService.subscribeArtist(this.artistId).subscribe(...)
    this.snackBar.open('Pretend we subscribed to Artist 🎉', 'Close', { duration: 3000 });
  }
}
