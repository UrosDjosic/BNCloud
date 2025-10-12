import { Component } from '@angular/core';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-content-upload',
  templateUrl: './content-upload.html',
  styleUrl: './content-upload.css',
  standalone: false
})
export class ContentUpload {

  uploads: SongUpload[] = [
    { genres: [], artists: [] } // start with one song
  ];

  constructor(private snackBar: MatSnackBar) {}

  onFileSelected(event: any, index: number) {
    const file: File = event.target.files[0];
    if (file) {
      const song = this.uploads[index];
      song.file = file;
      song.fileName = file.name;
      song.fileType = file.type;
      song.fileSize = file.size;
      song.creationTime = new Date(); // browser doesn't expose true creation time
      song.modificationTime = file.lastModified ? new Date(file.lastModified) : new Date();
    }
  }

  onImageSelected(event: any, index: number) {
    const file: File = event.target.files[0];
    if (file) {
      this.uploads[index].image = file;
    }
  }

  addAnotherSong() {
    this.uploads.push({ genres: [], artists: [] });
  }

  removeSong(index: number) {
    this.uploads.splice(index, 1);
  }

  submit() {
    // Call backend
    // this.contentService.uploadContent(this.uploads).subscribe({
    //   next: res => this.snackBar.open('Upload successful!', 'Close', { duration: 3000 }),
    //   error: err => this.snackBar.open('Upload failed.', 'Close', { duration: 3000 })
    // });

    this.snackBar.open('Dummy: Upload attempted', 'Close', { duration: 3000 });
    console.log(this.uploads);
  }
}

interface SongUpload {
  file?: File;
  fileName?: string;
  fileType?: string;
  fileSize?: number;
  creationTime?: Date;
  modificationTime?: Date;
  name?: string;
  genres: string[];
  image?: File;
  artists: string[]; // could be IDs or names
}
