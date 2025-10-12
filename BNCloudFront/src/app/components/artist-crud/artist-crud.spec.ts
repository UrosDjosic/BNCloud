import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ArtistCrud } from './artist-crud';

describe('ArtistCrud', () => {
  let component: ArtistCrud;
  let fixture: ComponentFixture<ArtistCrud>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ArtistCrud]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ArtistCrud);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
