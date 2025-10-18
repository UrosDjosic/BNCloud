import { Component } from '@angular/core';
import {FormBuilder} from '@angular/forms';
import {MatSnackBar} from '@angular/material/snack-bar';
import {OnInit} from '@angular/core';
import {ArtistDTO} from '../../models/artist';
import {Validators} from '@angular/forms';
import {ArtistService} from '../../services/artist-service';
import {GenreResponse} from '../../dto/genre-response';
import {GenreService} from '../../services/genre-service';

@Component({
  selector: 'app-artist-crud',
  templateUrl: './artist-crud.html',
  styleUrl: './artist-crud.css',
  standalone: false
})
export class ArtistCrud implements OnInit {

  isCreating: boolean = false; // toggle between create and update/delete
  displayedArtists: ArtistDTO[] = [];
  availableGenres: GenreResponse[] = [];
  selectedGenres: GenreResponse[] = [];
  lastKey : string = '';
  pageSize = 3;
  hasMore = true;
  loading = false;
  selectedArtist?: ArtistDTO;

  createForm: any;
  updateForm: any;

  constructor(
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
    private artistService: ArtistService,
    private genreService : GenreService
  ) {}

  ngOnInit() {
    // Forms
    this.createForm = this.fb.group({
      name: ['', Validators.required],
      biography: ['', Validators.required],
      genres: ['']
    });

    this.updateForm = this.fb.group({
      name: ['', Validators.required],
      biography: ['', Validators.required],
      genres: ['']
    });

    this.fetchArtists(); //async, be careful
    this.fetchGenres();
  }

  toggleView() {
    this.isCreating = !this.isCreating;
    this.selectedArtist = undefined; // reset selection
  }

  // Fodder methods
  fetchArtists() {
    if (!this.hasMore || this.loading) return;
    this.loading = true;
    this.artistService.getArtists(this.lastKey, this.pageSize).subscribe(res => {
      this.displayedArtists.push(...res.items);
      this.lastKey = res.lastKey;
      this.hasMore = !!res.lastKey;
      this.loading = false;
    });
  }

  selectArtist(artist: ArtistDTO) {
    this.selectedArtist = artist;
    this.updateForm.patchValue({
      name: artist.name,
      biography: artist.biography
    });
    this.selectedGenres = artist.genres;
  }

  createArtist() {
    if (this.createForm.invalid) {
      this.snackBar.open('Please fill all fields', 'Close', { duration: 3000 });
      return;
    }

    const formValue = this.createForm.value;

    let genres: GenreResponse[] = [...this.selectedGenres];

    if (formValue.genres && formValue.genres.trim() !== '') {
      genres = [
        ...genres,
        ...formValue.genres
          .split(',')
          .map((g: string) => ({ name: g.trim(), id: '' }))
          .filter((g: { name: string; id: string }) => g.name !== '')
      ];
    }
    this.artistService.create({
      name: formValue.name,
      genres: genres,
      biography : formValue.biography
    }).subscribe({
      next: () => {
        this.snackBar.open('Artist created successfully!', 'Close', { duration: 3000 });
        this.createForm.reset();
      },
      error: (err) => {
        console.error(err);
        this.snackBar.open('Failed to create artist', 'Close', { duration: 3000 });
      }
    })

    this.createForm.reset();
    this.fetchArtists(); // refresh list
    this.toggleView(); // go back to update/delete view
  }

  updateArtist() {
    if (!this.selectedArtist || this.updateForm.invalid) return;


    const formValue = this.updateForm.value;

    let genres: GenreResponse[] = [...this.selectedGenres];

    if (formValue.genres && formValue.genres.trim() !== '') {
      genres = [
        ...genres,
        ...formValue.genres
          .split(',')
          .map((g: string) => ({ name: g.trim(), id: '' }))
          .filter((g: { name: string; id: string }) => g.name !== '')
      ];
    }
    this.artistService.updateArtist({
      id: this.selectedArtist.id,
      name: formValue.name,
      genres: genres,
      biography: formValue.biography
    }).subscribe({
      next: (res: any) => {
        const updatedArtist: ArtistDTO = {
          id: res.artist.id,
          name: res.artist.name,
          biography: res.artist.biography,
          genres: res.artist.genres
        };

        this.snackBar.open(`Successfully updated "${updatedArtist.name}" ✏️!`, 'Close', { duration: 3000 });

        const index = this.displayedArtists.findIndex(a => a.id === updatedArtist.id);
        if (index !== -1) {
          this.displayedArtists[index] = updatedArtist;
        }

        this.selectedArtist = undefined;
        this.updateForm.reset();
        this.fetchGenres();
      },
      error: (err) => {
        console.error(err);
        this.snackBar.open(`Failed to update artist`, 'Close', { duration: 3000 });
      }
    });

  }

  deleteArtist() {
    if (!this.selectedArtist) return;

    // this.artistService.delete(this.selectedArtist.id).subscribe({ ... });
    this.snackBar.open(`Pretend we deleted artist "${this.selectedArtist.name}" ❌`, 'Close', { duration: 3000 });
    this.selectedArtist = undefined;
    this.fetchArtists();
  }
  onScroll(event: any) {
    const element = event.target;
    if (element.scrollHeight - element.scrollTop === element.clientHeight) {
      this.fetchArtists();
  }

  }

  private fetchGenres() {
    this.genreService.getAll().subscribe(res => {
      this.availableGenres = res.genres;
      console.log(res);
    })
  }

  toggleGenre(genre: GenreResponse) {
    console.log(this.availableGenres);
    const exists = this.selectedGenres.some(g => g.id === genre.id);

    if (exists) {
      this.selectedGenres = this.selectedGenres.filter(g => g.id !== genre.id);
    } else {
      this.selectedGenres.push(genre);
    }
  }

  isSelected(genre: GenreResponse): boolean {
    return this.selectedGenres.some(g => g.id === genre.id);
  }
}
