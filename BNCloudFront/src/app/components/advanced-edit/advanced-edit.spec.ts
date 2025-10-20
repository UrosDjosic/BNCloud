import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdvancedEdit } from './advanced-edit';

describe('AdvancedEdit', () => {
  let component: AdvancedEdit;
  let fixture: ComponentFixture<AdvancedEdit>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdvancedEdit]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdvancedEdit);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
