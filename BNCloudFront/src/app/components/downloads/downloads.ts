import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';

@Component({
  selector: 'app-downloads',
  templateUrl: './downloads.html',
  styleUrl: './downloads.css',
  standalone: false
})

export class Downloads implements OnInit {

  downloadedSongs: S[] = [];

  constructor(private router: Router) {}

  ngOnInit() {
    this.loadDownloads();
  }

  loadDownloads() {
    // this.downloadsService.getUserDownloads().subscribe(res => this.downloadedSongs = res);
    // then, it quickly casts them into S for simplicity (maybe)

    // Dummy data
    this.downloadedSongs = [
      { id: 's1', name: 'Rising Dawn', size: '5 MB' },
      { id: 's2', name: 'Fading Lights', size: '7.2 MB' },
      { id: 's3', name: 'Electric Dreams', size: '6.4 MB' }
    ];
  }

  navigateToSong(songId: string) {
    this.router.navigate([`/song/${songId}`]);
  }
}

interface S {
  id: string;
  name: string;
  size: string;
}
