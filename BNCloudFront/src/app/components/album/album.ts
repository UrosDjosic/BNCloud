import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AlbumService } from '../../services/album-service';
import { ArtistService } from '../../services/artist-service';
import { AlbumDTO } from '../../models/album';

@Component({
  selector: 'app-album',
  templateUrl: './album.html',
  styleUrls: ['./album.css'],
  standalone: false
})
export class Album implements OnInit {

  albumId?: string;
  album?: AlbumDTO;
  artistNames: { [id: string]: string } = {};
  editingName = false;
  editedName = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private albumService: AlbumService,
    private artistService: ArtistService
  ) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.albumId = params.get('albumId') || undefined;
      if (this.albumId) {
        this.loadAlbum(this.albumId);
      }
    });
  }

  async loadAlbum(id: string) {
    this.albumService.getAlbum(id).subscribe(async (res: any) => {
      console.log('Album loaded:', res);

      const album: AlbumDTO = {
        id: res.id,
        name: res.name,
        genres: res.genres || [],
        author: res.author || { id: '', name: '' },
        songs: (res.songs || []).map((s: any) => ({
          id: s.id,
          name: s.name,
          fileName: s.audioKey?.split('/').at(-1) || s.fileName,
          artists: s.artists
        }))
      };

      // Load artist names
      const artistIds = [
        album.author.id,
        ...album.songs.flatMap(s => s.artists || [])
      ].filter((id): id is string => !!id);

      await this.loadArtistNames(Array.from(new Set(artistIds)));
      console.log('Artist names loaded', this.artistNames);

      this.album = album;
    });
  }

  async downloadFromS3(presignedUrl: string): Promise<Blob> {
    return new Promise<Blob>((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('GET', presignedUrl, true);
      xhr.responseType = 'blob';

      xhr.onload = () => xhr.status >= 200 && xhr.status < 300
        ? resolve(xhr.response)
        : reject(new Error(`S3 download failed with status ${xhr.status}`));

      xhr.onerror = () => reject(new Error('Network error during S3 download'));
      xhr.send();
    });
  }

  async loadArtistNames(ids: string[]) {
    const artists = await Promise.all(ids.map(id => this.artistService.getArtist(id).toPromise()));
    const newArtistNames: { [id: string]: string } = {};
    artists.forEach((a: any) => newArtistNames[a.id] = a.name);
    this.artistNames = newArtistNames;
  }

  startEditing() {
    this.editingName = true;
    this.editedName = this.album?.name || '';
  }

  cancelEditing() {
    this.editingName = false;
  }

  saveName() {
    if (!this.album || !this.albumId) return;

    const newName = this.editedName.trim();
    if (!newName) return;

    this.albumService.updateAlbum(this.albumId, { name: newName }).subscribe({
      next: () => {
        if (this.album) this.album.name = newName;
        this.editingName = false;
        console.log('Album name updated successfully');
      },
      error: (err) => console.error('Error updating album:', err)
    });
  }

  navigateToArtist(artistId: string) {
    this.router.navigate([`/author/${artistId}`]);
  }

  navigateToSong(songId: string) {
    this.router.navigate([`/song/${songId}`]);
  }
}
