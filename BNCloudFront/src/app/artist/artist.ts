import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {ArtistDTO} from '../models/artist';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-artist',
  templateUrl: './artist.html',
  styleUrl: './artist.css',
  standalone: false
})
export class Artist implements OnInit {

  artistId?: string;
  artist?: ArtistDTO;

  constructor(private route: ActivatedRoute, private snackBar: MatSnackBar) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.artistId = params.get('artistId') || undefined;
      if (this.artistId) {
        this.artist = {
          id: this.artistId,
          name: 'The Midnight Beats',
          biography: 'An experimental indie rock band blending electronic and acoustic sounds.',
          genres: ['Indie Rock', 'Electronic', 'Experimental']
        };
      }
    });
  }

  subscribeArtist() {
    // this.userService.subscribeArtist(this.artistId).subscribe(...)
    this.snackBar.open('Pretend we subscribed to Artist 🎉', 'Close', { duration: 3000 });
  }
}
