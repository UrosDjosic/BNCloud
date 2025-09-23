import {Component, OnInit} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {SearchResult} from '../models/search-result';
import {ActivatedRoute, Router} from '@angular/router';

@Component({
  selector: 'app-search',
  templateUrl: './search.html',
  styleUrl: './search.css',
  standalone: false
})
export class Search implements OnInit {

  searchForm: any;
  results: SearchResult[] = [];

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {

    this.searchForm = this.fb.group({
      type: ['song', Validators.required],
      query: ['', Validators.required]
    });

    this.route.queryParams.subscribe(params => {
      const type = params['type'];
      const query = params[type];

      if (type && query) {
        this.searchForm.patchValue({ type, query });
        this.fetchResults(type, query);
      }
    });
  }

  onSearch() {
    if (this.searchForm.invalid) return;

    const { type, query } = this.searchForm.value;

    // Update URL
    this.router.navigate(['/search'], { queryParams: { type, [type]: query } });

    // Fetch results
    this.fetchResults(type, query);
  }

  fetchResults(type: string, query: string) {
    // Example: fetch from backend
    // this.searchService.search(type, query).subscribe(res => this.results = res);

    // Dummy data
    this.results = [
      { id: '1', type: type as any, name: `${query} Result 1` },
      { id: '2', type: type as any, name: `${query} Result 2` },
      { id: '3', type: type as any, name: `${query} Result 3` }
    ];
  }

  navigate(item: SearchResult) {
    switch (item.type) {
      case 'song':
        this.router.navigate([`/song/${item.id}`]);
        break;
      case 'album':
        this.router.navigate([`/album/${item.id}`]);
        break;
      case 'artist':
        this.router.navigate([`/author/${item.id}`]);
        break;
      case 'genre':
        this.router.navigate(['/search'], { queryParams: { genre: item.name } });
        break;
    }
  }
}
