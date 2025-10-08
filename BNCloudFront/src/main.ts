import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppConfig } from './app/app.module';

platformBrowserDynamic()
  .bootstrapModule(AppConfig)
  .catch(err => console.error(err));
