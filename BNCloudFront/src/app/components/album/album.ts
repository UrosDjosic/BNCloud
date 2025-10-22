import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AlbumService } from '../../services/album-service';
import { ArtistService } from '../../services/artist-service';
import { AlbumDTO } from '../../models/album';
import {ConfirmDialogComponent} from '../confirm-dialog/confirm-dialog.component';
import {MatSnackBar} from '@angular/material/snack-bar';
import {MatDialog} from '@angular/material/dialog';

@Component({
  selector: 'app-album',
  templateUrl: './album.html',
  styleUrls: ['./album.css'],
  standalone: false
})
export class Album implements OnInit {

  albumId?: string;
  album?: any;
  editingName = false;
  editedName = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private albumService: AlbumService,
    private dialog: MatDialog,
    private snackbar: MatSnackBar
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

      this.album = {
        id: res.id,
        name: res.name,
        genres: res.genres || [],
        author: res.authors || { id: '', name: '' },
        songs: (res.songs || []).map((s: any) => ({
          id: s.id,
          name: s.name,
          fileName: s.audioKey?.split('/').at(-1) || s.fileName,
          artists: s.artists
        }))
      };
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

  deleteAlbum() {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: { message: 'Are you sure you want to delete this album?' }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.albumService.deleteAlbum(this.albumId!).subscribe({
          next: () => {
            this.snackbar.open('Album deleted successfully.', 'OK', { duration: 3000 });
            this.router.navigate(['/albums']);
          },
          error: (err) => {
            console.error('Error deleting album:', err);
            this.snackbar.open('Failed to delete album.', 'Close', { duration: 3000 });
          }
        });
      }
    });
  }

  navigateToArtist(artistId: string) {
    this.router.navigate([`/artist/${artistId}`]);
  }

  navigateToSong(songId: string) {
    this.router.navigate([`/song/${songId}`]);
  }
}
