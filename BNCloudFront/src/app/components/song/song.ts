import {Component, OnInit} from '@angular/core';
import {SongDTO} from '../../models/song';
import {AlbumDTO} from '../../models/album';
import {ArtistDTO} from '../../models/artist';
import {ActivatedRoute, Router} from '@angular/router';

@Component({
  selector: 'app-song',
  templateUrl: './song.html',
  styleUrl: './song.css',
  standalone: false
})
export class Song implements OnInit {

  songId?: string;
  song?: SongDTO;

  constructor(private route: ActivatedRoute, private router: Router) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.songId = params.get('songId') || undefined;
      if (this.songId) {
        this.loadSong(this.songId);
      }
    });
  }

  loadSong(id: string) {
    // this.songService.getSongById(id).subscribe(res => this.song = res);

    // Dummy data
    this.song = {
      id: id,
      fileName: 'AmazingSong.mp3',
      fileType: 'audio/mp3',
      size: '5.2 MB',
      createdAt: '2024-05-10 12:00',
      updatedAt: '2024-08-15 15:30',
      authors: [],
      ratings: [2],
      genres: [''],
      image: ""
    };
  }

  subscribeSong() {
    // Placeholder
    // this.userService.subscribeSong(this.songId).subscribe(...)
    console.log('Subscribed to song');
  }

  addToUserList() {
    // Placeholder
    console.log('Added to user list');
  }

  downloadSong() {
    // Placeholder
    console.log('Downloading song file');
  }

  rateSong(stars: number) {
    if (this.song) this.song.ratings?.push(stars);
    // this.songService.rateSong(this.songId, stars).subscribe(...)
  }

  editSong() {
    // Navigate to song edit page or open dialog
    this.router.navigate(['content-rud']);
  }

  deleteSong() {
    // this.songService.deleteSong(this.songId).subscribe(...)
    console.log('Deleted song');
    this.router.navigate(['/search']);
  }

  navigateToArtist(artistId: string) {
    this.router.navigate([`/author/${artistId}`]);
  }

  navigateToAlbum(albumId: string) {
    this.router.navigate([`/album/${albumId}`]);
  }
}
