import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContentRud } from './content-rud';

describe('ContentRud', () => {
  let component: ContentRud;
  let fixture: ComponentFixture<ContentRud>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContentRud]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContentRud);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
