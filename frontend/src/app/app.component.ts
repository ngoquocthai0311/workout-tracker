import { Component } from '@angular/core';
import { RouterModule, RouterOutlet } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { Toast } from 'primeng/toast';
import { DrawerModule } from 'primeng/drawer';

@Component({
  selector: 'app-root',
  imports: [
    DrawerModule,
    Toast,
    RouterModule,
    RouterOutlet,
    ScrollPanelModule,
    ButtonModule,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'frontend';

  visibleSideBar: boolean = false;

  ngOnInit() {}
}
