import { Component } from '@angular/core';
import { RouterModule, RouterOutlet } from '@angular/router';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { Toast } from 'primeng/toast';

@Component({
  selector: 'app-root',
  imports: [Toast, RouterModule, RouterOutlet, ScrollPanelModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'frontend';

  ngOnInit() {}
}
