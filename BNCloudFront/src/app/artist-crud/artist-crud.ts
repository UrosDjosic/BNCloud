import { Component } from '@angular/core';
import {FormBuilder} from '@angular/forms';
import {MatSnackBar} from '@angular/material/snack-bar';
import {OnInit} from '@angular/core';
import {ArtistDTO} from '../models/artist';
import {Validators} from '@angular/forms';

@Component({
  selector: 'app-artist-crud',
  templateUrl: './artist-crud.html',
  styleUrl: './artist-crud.css',
  standalone: false
})
export class ArtistCrud implements OnInit {

  isCreating: boolean = false; // toggle between create and update/delete
  artists: ArtistDTO[] = []; // will hold list of artists for selection
  selectedArtist?: ArtistDTO;

  createForm: any;
  updateForm: any;

  constructor(
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit() {
    // Forms
    this.createForm = this.fb.group({
      name: ['', Validators.required],
      biography: ['', Validators.required],
      genres: ['', Validators.required]
    });

    this.updateForm = this.fb.group({
      name: ['', Validators.required],
      biography: ['', Validators.required],
      genres: ['', Validators.required]
    });

    this.fetchArtists(); //async, be careful
  }

  toggleView() {
    this.isCreating = !this.isCreating;
    this.selectedArtist = undefined; // reset selection
  }

  // Fodder methods
  fetchArtists() {
    // Example fetch
    // this.artistService.getAll().subscribe({ next: res => this.artists = res });
    this.artists = [
      { id: '1', name: 'Artist One', biography: 'Bio 1', genres: ['Pop', 'Rock'] },
      { id: '2', name: 'Artist Two', biography: 'Bio 2', genres: ['Jazz'] }
    ]; // dummy data
  }

  selectArtist(artist: ArtistDTO) {
    this.selectedArtist = artist;
    this.updateForm.patchValue({
      name: artist.name,
      biography: artist.biography,
      genres: artist.genres
    });
  }

  createArtist() {
    if (this.createForm.invalid) {
      this.snackBar.open('Please fill all fields', 'Close', { duration: 3000 });
      return;
    }

    const formValue = this.createForm.value;

    // this.artistService.create(formValue).subscribe({ ... });
    this.snackBar.open(`Pretend we created artist "${formValue.name}" 🎨`, 'Close', { duration: 3000 });
    this.createForm.reset();
    this.fetchArtists(); // refresh list
    this.toggleView(); // go back to update/delete view
  }

  updateArtist() {
    if (!this.selectedArtist || this.updateForm.invalid) return;

    const formValue = this.updateForm.value;

    // this.artistService.update(this.selectedArtist.id, formValue).subscribe({ ... });
    this.snackBar.open(`Pretend we updated artist "${formValue.name}" ✏️`, 'Close', { duration: 3000 });
    this.fetchArtists();
  }

  deleteArtist() {
    if (!this.selectedArtist) return;

    // this.artistService.delete(this.selectedArtist.id).subscribe({ ... });
    this.snackBar.open(`Pretend we deleted artist "${this.selectedArtist.name}" ❌`, 'Close', { duration: 3000 });
    this.selectedArtist = undefined;
    this.fetchArtists();
  }
}
