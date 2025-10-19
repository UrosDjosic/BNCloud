import {Component, OnInit} from '@angular/core';
import {AlbumDTO} from '../../models/album';
import {ActivatedRoute, Router} from '@angular/router';

@Component({
  selector: 'app-album',
  templateUrl: './album.html',
  styleUrl: './album.css',
  standalone: false
})
export class Album implements OnInit {

  albumId?: string;
  album?: AlbumDTO;

  constructor(private route: ActivatedRoute, private router: Router) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.albumId = params.get('albumId') || undefined;
      if (this.albumId) {
        this.loadAlbum(this.albumId);
      }
    });
  }

  loadAlbum(id: string) {
    // this.albumService.getAlbumById(id).subscribe(res => this.album = res);
  }

  navigateToArtist(artistId: string) {
    this.router.navigate([`/author/${artistId}`]);
  }

  navigateToSong(songId: string) {
    this.router.navigate([`/song/${songId}`]);
  }
}
