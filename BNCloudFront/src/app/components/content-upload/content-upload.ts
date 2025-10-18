import {Component, OnInit} from '@angular/core';
import {MatSnackBar} from '@angular/material/snack-bar';
import {ArtistDTO} from '../../models/artist';
import {ArtistService} from '../../services/artist-service';
import {SongService} from '../../services/song-service';
import {DynamoSongResponse} from '../../dto/dynamo-song-response';
import {AlbumService} from '../../services/album-service';

@Component({
  selector: 'app-content-upload',
  templateUrl: './content-upload.html',
  styleUrl: './content-upload.css',
  standalone: false
})
export class ContentUpload implements OnInit {
  uploads: SongUpload[] = [{ genres: [], artists: [], genresText: '', image: null, file: null }];
  artists: ArtistDTO[] = [];
  lastKey: string | null = null;

  constructor(private snackBar: MatSnackBar, private artistService: ArtistService, private ss: SongService, private as: AlbumService) {}

  ngOnInit(): void {
    this.loadArtists();
  }

  /** Fetch all artists to populate dropdown */
  loadArtists(lastKey: string = '', pageSize: number = 50): void {
    this.artistService.getArtists(lastKey, pageSize).subscribe({
      next: (response) => {
        // Append current batch of artists
        this.artists = [...this.artists, ...response.items];

        // If there’s another page, fetch it recursively
        if (response.lastKey) {
          this.loadArtists(response.lastKey, pageSize);
        } else {
          console.log(`Loaded all ${this.artists.length} artists`);
        }
      },
      error: (err) => {
        console.error('Failed to load artists', err);
        this.snackBar.open('Failed to load artists', 'Close', { duration: 3000 });
      },
    });
  }

  /** Handle audio file selection */
  onFileSelected(event: any, index: number): void {
    const file: File = event.target.files[0];
    if (file && file.size < 10*1024*1024) {
      const song = this.uploads[index];
      song.file = file;
      song.fileName = file.name;
      song.fileType = file.type;
      song.fileSize = file.size;
      song.creationTime = new Date();
      song.modificationTime = file.lastModified ? new Date(file.lastModified) : new Date();
    }
    else {
      this.snackBar.open("You must upload a file smaller than 10MB!")
    }
  }

  /** Handle cover image upload */
  onImageSelected(event: any, index: number): void {
    const file: File = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        this.uploads[index].imagePreview = reader.result as string;
      };
      reader.readAsDataURL(file);
      this.uploads[index].image = file;

      console.log(this.uploads[index]);
    }
  }

  /** Convert comma-separated text to array */
  updateGenres(index: number): void {
    const song = this.uploads[index];
    song.genres = song.genresText
      ? song.genresText.split(',').map((g) => g.trim()).filter((g) => g)
      : [];
  }

  /** Add another song input block */
  addAnotherSong(): void {
    this.uploads.push({ genres: [], artists: [], genresText: '', image: null, file: null});
  }

  /** Remove one song entry */
  removeSong(index: number): void {
    this.uploads.splice(index, 1);
  }

  async submit(): Promise<void> {
    if (this.uploads.length === 1) {
      const upload = this.uploads[0];

      const song = {
        name: upload.name,
        genres: upload.genres,
        artists: upload.artists,
        creationTime: upload.creationTime,
        modificationTime: upload.modificationTime,
        ratings: [],
        audioFileName: upload.fileName,
        imageFileName: upload.image!.name,
      };

      this.ss.uploadSongMetadata(song).subscribe({
        next: async (response: DynamoSongResponse) => {
          await Promise.all([
            this.uploadToS3(upload.file!, response.audioUploadUrl),
            this.uploadToS3(upload.image!, response.imageUploadUrl)
          ]);
          this.snackBar.open('Song uploaded successfully', 'Close', { duration: 3000 });
        },
        error: (err) => {
          console.error(err);
          this.snackBar.open('Failed to upload song', 'Close', { duration: 3000 });
        }
      });
    } else {
      try {
        // 1️⃣ Upload all songs metadata + files in parallel
        const uploadResults = await Promise.all(
          this.uploads.map(async (upload) => {
            const song = {
              name: upload.name,
              genres: upload.genres,
              artists: upload.artists,
              creationTime: upload.creationTime,
              modificationTime: upload.modificationTime,
              ratings: [],
              audioFileName: upload.fileName,
              imageFileName: upload.image!.name,
            };

            return new Promise<string>((resolve, reject) => {
              this.ss.uploadSongMetadata(song).subscribe({
                next: async (response: DynamoSongResponse) => {
                  try {
                    await Promise.all([
                      this.uploadToS3(upload.file!, response.audioUploadUrl),
                      this.uploadToS3(upload.image!, response.imageUploadUrl)
                    ]);
                    resolve(response.songId);
                  } catch (uploadErr) {
                    reject(uploadErr);
                  }
                },
                error: (err) => reject(err)
              });
            });
          })
        );

        // 2️⃣ Aggregate genres & artists across all uploads
        const allGenres = [
          ...new Set(this.uploads.flatMap((u) => u.genres))
        ];
        const allArtists = [
          ...new Set(this.uploads.flatMap((u) => u.artists))
        ];

        // 3️⃣ Create album object
        const album = {
          name: this.uploads[0].name || 'Untitled Album',
          genres: allGenres,
          artists: allArtists,
          songs: uploadResults, // IDs returned from uploadSongMetadata
        };

        // 4️⃣ Upload album
        this.as.uploadAlbum(album).subscribe({
          next: (response: string) => {
            console.log('Album created:', response);
            this.snackBar.open('Album uploaded successfully', 'Close', { duration: 3000 });
          },
          error: (err) => {
            console.error('Album creation failed', err);
            this.snackBar.open('Failed to create album', 'Close', { duration: 3000 });
          }
        });
      } catch (err) {
        console.error('One or more song uploads failed:', err);
        this.snackBar.open('Some songs failed to upload', 'Close', { duration: 3000 });
      }
    }
  }


  async uploadToS3(file: File, presignedUrl: string): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.open('PUT', presignedUrl, true);

      // Optional progress listener (for upload bars later)
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          console.log(`Upload progress: ${percent}%`);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          console.log('Upload succeeded:', xhr.status);
          resolve();
        } else {
          console.error('Upload failed:', xhr.status, xhr.responseText);
          reject(new Error(`S3 upload failed with status ${xhr.status}`));
        }
      };

      xhr.onerror = () => {
        console.error('Network error during S3 upload');
        reject(new Error('Network error during S3 upload'));
      };

      // ⚠️ Don’t set Content-Type header here — this avoids the 403 error
      xhr.send(file);
    });
  }

}

interface SongUpload {
  file: File | null;
  fileName?: string;
  fileType?: string;
  fileSize?: number;
  creationTime?: Date;
  modificationTime?: Date;
  name?: string;
  genres: string[];
  genresText?: string;
  image: File | null;
  imagePreview?: string;
  artists: string[]; // will store selected artist IDs
}
