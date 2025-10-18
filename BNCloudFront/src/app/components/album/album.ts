import {Component, OnInit} from '@angular/core';
import {AlbumDTO} from '../../models/album';
import {ActivatedRoute, Router} from '@angular/router';
import {SongDTO} from '../../models/song';
import {ArtistDTO} from '../../models/artist';

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

    // Dummy data
    this.album = {
      id: id,
      name: 'Echoes of Tomorrow',
      genres: [],
      author: {
        id: 'a1', name: 'The Midnight Beats',
        biography: '',
        genres: []
      },
      songs: [
        {
          id: 's1', fileName: 'Rising Dawn',
          fileType: '',
          size: '',
          createdAt: '',
          updatedAt: '',
          genres: [''],
          authors: [],
          image: ""
        },
        {
          id: 's2', fileName: 'Fading Lights',
          fileType: '',
          size: '',
          createdAt: '',
          updatedAt: '',
          genres: [''],
          authors: [],
          image: ""
        },
        {
          id: 's3', fileName: 'Electric Dreams',
          fileType: '',
          size: '',
          createdAt: '',
          updatedAt: '',
          genres: [''],
          authors: [],
          image: ""
        }
      ]
    };
  }

  navigateToArtist(artistId: string) {
    this.router.navigate([`/author/${artistId}`]);
  }

  navigateToSong(songId: string) {
    this.router.navigate([`/song/${songId}`]);
  }
}
