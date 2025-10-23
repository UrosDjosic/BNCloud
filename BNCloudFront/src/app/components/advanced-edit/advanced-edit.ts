import {Component, ViewChild} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {CommonModule, DatePipe, DecimalPipe, NgForOf, NgIf} from '@angular/common';
import {MatCard} from '@angular/material/card';
import {MatSnackBar} from '@angular/material/snack-bar';
import {SongService} from '../../services/song-service';
import {ElementRef} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {MatProgressBar} from '@angular/material/progress-bar';

@Component({
  selector: 'app-advanced-edit',
  imports: [
    MatCard,
    DatePipe,
    DecimalPipe,
    FormsModule,
    CommonModule,
    MatProgressBar
  ],
  templateUrl: './advanced-edit.html',
  styleUrl: './advanced-edit.css'
})
export class AdvancedEdit {
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  songId?: any;
  audio?: any;
  image?: any;
  song: any = {};

  newAudio: any = {};
  newCover: any = {};

  totalProgress: number = 0;
  isUploading: boolean = false;
  private uploadProgressMap = new Map<string, number>();

  constructor(private router: Router, private route: ActivatedRoute, private snackBar: MatSnackBar, private ss: SongService) {}
  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.songId = params.get('songId');
      const audioUrl = decodeURIComponent(params.get('audioUrl')!);
      const imageUrl = decodeURIComponent(params.get('imageUrl')!);
      console.log(audioUrl);
      this.audio = audioUrl.split("/").at(-1);
      (async () => {
        try {
          const [imageBlob] = await Promise.all([
            this.downloadFromS3(imageUrl)
          ]);
          this.image = URL.createObjectURL(imageBlob);
        } catch (err) {
          console.error('Error downloading media from S3', err);
        }
      })();
    });
  }

  onFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (file && file.size < 10*1024*1024) {
      this.song.file = file;
      this.song.fileName = file.name;
      this.song.fileType = file.type;
      this.song.fileSize = file.size;
      this.song.modificationTime = new Date(file.lastModified);
    }
    else {
      this.snackBar.open("You must upload a file smaller than 10MB!")
    }
  }

  updateAudio() {
    this.newAudio.file = this.song.fileName;
    this.newAudio.songId = this.songId;
    this.ss.audioUpdate(this.newAudio).subscribe(async (res: any) => {
      try {
        const deleteOldUrl = res.deleteOldUrl; // presigned URL for DELETE
        const uploadNewUrl = res.uploadNewUrl; // presigned URL for PUT
        const newFile = this.song.file; // Blob/File to upload

        // 1️⃣ Delete old file/folder
        console.log('Deleting old audio...');
        await this.deleteFromS3(deleteOldUrl);
        console.log('Old audio deleted.');

        // 2️⃣ Upload new file
        console.log('Uploading new audio...');
        await this.uploadToS3(uploadNewUrl, newFile);
        console.log('New audio uploaded successfully.');

        this.router.navigate(['/discover']);

        // Optionally, notify the user that update succeeded
      } catch (error) {
        console.error('Error updating audio:', error);
        // Optionally, show an error message to the user
      } finally {
        this.isUploading = false;
        this.uploadProgressMap.clear();
        this.totalProgress = 0;
      }
    })
  }

  updateImage() {
    const input = this.fileInput.nativeElement;

    if (input.files && input.files.length > 0) {
      this.newCover.image = input.files[0].name;
      console.log('Selected image:', this.image);
    } else {
      console.log('No image selected');
    }
    this.newCover.songId = this.songId;
    this.ss.imageUpdate(this.newCover).subscribe(async (res: any) => {
      try {
        const deleteOldUrl = res.deleteOldUrl; // presigned URL for DELETE
        const uploadNewUrl = res.uploadNewUrl; // presigned URL for PUT
        const newFile = input.files![0]; // Blob/File to upload

        // 1️⃣ Delete old file/folder
        console.log('Deleting old image...');
        await this.deleteFromS3(deleteOldUrl);
        console.log('Old image deleted.');

        // 2️⃣ Upload new file
        console.log('Uploading new image...');
        await this.uploadToS3(uploadNewUrl, newFile);
        console.log('New image uploaded successfully.');

        this.router.navigate(['/discover']);

        // Optionally, notify the user that update succeeded
      } catch (error) {
        console.error('Error updating image:', error);
        // Optionally, show an error message to the user
      } finally {
        this.isUploading = false;
        this.uploadProgressMap.clear();
        this.totalProgress = 0;
      }
    })
  }

  // S3 shananigans
  async deleteFromS3(presignedUrl: string): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.open('DELETE', presignedUrl, true);

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          console.log('Delete succeeded:', xhr.status);
          resolve(); // nothing to return for delete
        } else {
          console.error('Delete failed:', xhr.status, xhr.responseText);
          reject(new Error(`S3 delete failed with status ${xhr.status}`));
        }
      };

      xhr.onerror = () => {
        console.error('Network error during S3 delete');
        reject(new Error('Network error during S3 delete'));
      };

      xhr.send(); // DELETE request typically has no body
    });
  }

  async downloadFromS3(presignedUrl: string): Promise<Blob> {
    return new Promise<Blob>((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.open('GET', presignedUrl, true);
      xhr.responseType = 'blob'; // ensures we get a Blob

      // Optional progress listener
      xhr.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          console.log(`Download progress: ${percent}%`);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          console.log('Download succeeded:', xhr.status);
          resolve(xhr.response); // this is the Blob
        } else {
          console.error('Download failed:', xhr.status, xhr.responseText);
          reject(new Error(`S3 download failed with status ${xhr.status}`));
        }
      };

      xhr.onerror = () => {
        console.error('Network error during S3 download');
        reject(new Error('Network error during S3 download'));
      };

      xhr.send(); // no body for GET
    });
  }

  async uploadToS3(presignedUrl: string, file: Blob | File): Promise<void> {
    this.isUploading = true;

    return new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('PUT', presignedUrl, true);

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          this.setFileProgress(file instanceof File ? file.name : 'file', percent);
          console.log(`Upload progress: ${percent}%`);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          this.setFileProgress(file instanceof File ? file.name : 'file', 100);
          resolve();
        } else {
          reject(new Error(`S3 upload failed: ${xhr.status}`));
        }
      };

      xhr.onerror = () => reject(new Error('Network error during S3 upload'));
      xhr.send(file);
    });
  }


  setFileProgress(fileName: string, percent: number) {
    this.uploadProgressMap.set(fileName, percent);

    const values = Array.from(this.uploadProgressMap.values());
    const avgProgress = Math.round(values.reduce((a, b) => a + b, 0) / values.length);

    this.totalProgress = avgProgress;
  }
}
